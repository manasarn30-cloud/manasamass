import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from support.models import FAQ, SupportTicket
from support.forms import SupportTicketForm
from support.assistant import process_user_message
from support.mongo import log_chat_feedback

logger = logging.getLogger('streamflix')


def faq_view(request):
    """
    Displays frequently asked questions from the SQL database.
    Supports category filtering and question search.
    """
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    faqs = FAQ.objects.filter(is_active=True)

    if search_query:
        faqs = faqs.filter(
            Q(question__icontains=search_query) |
            Q(answer__icontains=search_query) |
            Q(keywords__icontains=search_query)
        )

    if selected_category and selected_category != 'All':
        faqs = faqs.filter(category=selected_category)

    # Group by category for structured help-center display
    categories = [
        'All',
        'Account & Authentication',
        'Streaming & Playback',
        'Lists & Navigation',
        'Platform Errors & Status Codes',
        'Support & Technical Diagnostics',
    ]

    context = {
        'faqs': faqs,
        'search_query': search_query,
        'selected_category': selected_category or 'All',
        'categories': categories,
        'total_faqs': faqs.count(),
    }
    return render(request, 'support/faq.html', context)


def support_ticket_list_view(request):
    """
    Support Desk:
    - Lists authenticated user's submitted tickets.
    - Provides ticket creation form.
    """
    form = SupportTicketForm()

    user_tickets = []
    if request.user.is_authenticated:
        user_tickets = SupportTicket.objects.filter(user=request.user)
    else:
        # Check session for any guest ticket references
        session_tickets = request.session.get('guest_tickets', [])
        if session_tickets:
            user_tickets = SupportTicket.objects.filter(reference_number__in=session_tickets)

    context = {
        'form': form,
        'user_tickets': user_tickets,
        'total_tickets': len(user_tickets),
    }
    return render(request, 'support/support.html', context)


@require_POST
def create_ticket_view(request):
    """Handles submission of a new support ticket."""
    form = SupportTicketForm(request.POST)
    if form.is_valid():
        ticket = form.save(commit=False)
        if request.user.is_authenticated:
            ticket.user = request.user
            if not ticket.guest_email and request.user.email:
                ticket.guest_email = request.user.email
        ticket.source = 'Web Form'
        ticket.save()

        # Track guest tickets in session
        if not request.user.is_authenticated:
            guest_tickets = request.session.get('guest_tickets', [])
            guest_tickets.append(ticket.reference_number)
            request.session['guest_tickets'] = guest_tickets

        logger.info(f"Support ticket created: {ticket.reference_number} by {request.user.username if request.user.is_authenticated else 'Guest'}")
        messages.success(request, f"Support ticket #{ticket.reference_number} created successfully. Our team will review it shortly.")
        return redirect('ticket_detail', reference_number=ticket.reference_number)
    else:
        messages.error(request, "Please check the form errors below.")
        user_tickets = SupportTicket.objects.filter(user=request.user) if request.user.is_authenticated else []
        return render(request, 'support/support.html', {'form': form, 'user_tickets': user_tickets})


def support_ticket_detail_view(request, reference_number):
    """
    Displays ticket details and status.
    Enforces authorization: only owner, session guest, or staff can view!
    """
    ticket = get_object_or_404(SupportTicket, reference_number=reference_number)

    # Authorization verification
    is_owner = False
    if request.user.is_authenticated:
        if ticket.user == request.user or request.user.is_staff:
            is_owner = True
    else:
        session_tickets = request.session.get('guest_tickets', [])
        if ticket.reference_number in session_tickets:
            is_owner = True

    if not is_owner:
        logger.warning(f"Unauthorized access attempt to ticket {reference_number} by {request.user}")
        raise PermissionDenied("You do not have permission to view this support ticket.")

    context = {
        'ticket': ticket,
    }
    return render(request, 'support/ticket_detail.html', context)


@require_POST
def chatbot_api_view(request):
    """
    API endpoint for the floating AI assistant.
    Receives JSON payload: { message: str, conversation_id: str, state: str }
    Returns assistant answer, error explanation, or ticket escalation.
    """
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        body = request.POST

    message = body.get('message', '').strip()
    conversation_id = body.get('conversation_id', '').strip()
    previous_state = body.get('state', '').strip()

    if not message:
        return JsonResponse({'error': 'Message content cannot be empty.'}, status=400)

    # Length protection
    if len(message) > 1000:
        return JsonResponse({'error': 'Message exceeds maximum length of 1000 characters.'}, status=400)

    session_id = request.session.session_key
    if not session_id:
        request.session.save()
        session_id = request.session.session_key

    result = process_user_message(
        user_message=message,
        conversation_id=conversation_id,
        user=request.user,
        session_id=session_id,
        previous_state=previous_state
    )

    return JsonResponse(result)


@require_POST
def chatbot_feedback_api_view(request):
    """
    API endpoint to record user feedback on assistant responses.
    Saves to MongoDB chat_feedback collection.
    """
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        body = request.POST

    conversation_id = body.get('conversation_id', '').strip()
    message_id = body.get('message_id', '').strip()
    rating = body.get('rating', '').strip()  # 'helpful' or 'not_helpful'
    feedback_text = body.get('feedback_text', '').strip()

    if rating not in ('helpful', 'not_helpful'):
        return JsonResponse({'error': 'Rating must be either helpful or not_helpful.'}, status=400)

    user_id = request.user.id if request.user.is_authenticated else None
    logged = log_chat_feedback(
        conversation_id=conversation_id,
        message_id=message_id,
        rating=rating,
        feedback_text=feedback_text,
        user_id=user_id
    )

    return JsonResponse({'success': True, 'persisted_in_mongodb': logged})
