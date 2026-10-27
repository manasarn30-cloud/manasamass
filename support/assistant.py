import re
import logging
from support.models import FAQ, SupportTicket
from support.mongo import log_chat_message

logger = logging.getLogger('streamflix')

# Accurate explanations for the 8 required HTTP/application error codes
ERROR_CODE_KNOWLEDGE = {
    "400": {
        "title": "HTTP 400: Bad Request",
        "meaning": "The server could not understand or process your request due to malformed syntax, invalid parameters, or corrupted browser data.",
        "causes": "Mistyped URL query parameters, expired or corrupted cookies, invalid form input, or oversized payload.",
        "what_to_try": "1. Clear your browser cookies and site cache for StreamFlix.\n2. Ensure all required form fields are properly filled.\n3. Return to the home page and retry.",
        "contact_support": "If a specific link or feature repeatedly triggers a 400 error despite clearing cache, file a support ticket."
    },
    "401": {
        "title": "HTTP 401: Unauthorized",
        "meaning": "Access to the requested resource requires valid user credentials, but none were provided or the session expired.",
        "causes": "Browsing protected areas (like My List or Ticket Details) while signed out, or session expiration.",
        "what_to_try": "1. Sign in with your registered username/email and password.\n2. If you don't have an account, click 'Sign Up' to create one for free.",
        "contact_support": "If your credentials are rejected repeatedly, request an account reset via Support."
    },
    "403": {
        "title": "HTTP 403: Forbidden",
        "meaning": "The server understood who you are, but you do not have permission to view or modify this specific resource.",
        "causes": "Attempting to inspect another user's private support ticket, modifying restricted database objects, or accessing admin tools without staff privileges.",
        "what_to_try": "1. Verify you are logged into the correct account.\n2. Return to your personal dashboard.",
        "contact_support": "If you believe you should have access to this resource, contact platform administration."
    },
    "404": {
        "title": "HTTP 404: Not Found",
        "meaning": "The server cannot find the requested web address or movie record.",
        "causes": "A typo in the URL path, an outdated bookmark, or a title that was removed or reorganized.",
        "what_to_try": "1. Double-check the URL spelling.\n2. Use the 'Discover' search bar to search for the movie title.\n3. Click 'Return Home' to continue browsing.",
        "contact_support": "If a button or link on StreamFlix points to a 404 page, please report it via ticket."
    },
    "429": {
        "title": "HTTP 429: Too Many Requests",
        "meaning": "You have sent too many requests in a given amount of time (rate limit triggered).",
        "causes": "Rapidly refreshing pages, automated scraping bots, or submitting forms dozens of times in seconds.",
        "what_to_try": "1. Wait 30 to 60 seconds before submitting another request.\n2. Refrain from automated rapid clicks or refresh loops.",
        "contact_support": "If rate limits persist under normal personal browsing, notify support."
    },
    "460": {
        "title": "Code 460: StreamFlix Application Diagnostic Error",
        "meaning": "A StreamFlix-specific application-level error (defined internally for system triage, NOT a standardized RFC HTTP status).",
        "causes": "Triggered during internal health diagnostics, service stress testing, or when an edge-case catalog integrity check fails.",
        "what_to_try": "1. Refresh the page to reload cached catalog state.\n2. Use our 'Discover' page to browse standard categories.",
        "contact_support": "Because 460 is an internal diagnostic code, reporting it helps our engineering team trace exact system events."
    },
    "500": {
        "title": "HTTP 500: Internal Server Error",
        "meaning": "The server encountered an unexpected situation that prevented it from fulfilling your request.",
        "causes": "Uncaught server-side exception, database lock, or misconfigured application component.",
        "what_to_try": "1. Refresh the page after 10-15 seconds.\n2. Our automated logging system immediately records 500 errors for review.",
        "contact_support": "If a page consistently crashes with 500, file a ticket including what action you performed."
    },
    "503": {
        "title": "HTTP 503: Service Unavailable",
        "meaning": "The server is temporarily unable to handle the request due to maintenance, server updates, or high traffic.",
        "causes": "Scheduled maintenance, transient database failover, or server bootup.",
        "what_to_try": "1. Wait a moment and try again.\n2. Check back in a few minutes.",
        "contact_support": "If downtime extends beyond scheduled maintenance windows, check our platform status."
    }
}


def detect_error_code(text):
    """
    Detects if the user query is asking about one of the 8 supported error codes.
    Returns the code string or None.
    """
    clean = text.lower()
    # Explicit code pattern matching
    match = re.search(r'\b(400|401|403|404|429|460|500|503)\b', clean)
    if match:
        return match.group(1)

    # Keyword checks
    if "bad request" in clean:
        return "400"
    if "unauthorized" in clean:
        return "401"
    if "forbidden" in clean:
        return "403"
    if "not found" in clean or "missing page" in clean:
        return "404"
    if "too many requests" in clean or "rate limit" in clean:
        return "429"
    if "streamflix error" in clean or "diagnostic error" in clean:
        return "460"
    if "internal server error" in clean or "server error" in clean:
        return "500"
    if "service unavailable" in clean or "server down" in clean:
        return "503"

    return None


def format_error_explanation(code):
    """Formats a structured, human-readable error explanation."""
    info = ERROR_CODE_KNOWLEDGE.get(code)
    if not info:
        return None

    return (
        f"**{info['title']}**\n\n"
        f"• **What it means:** {info['meaning']}\n"
        f"• **Common causes:** {info['causes']}\n"
        f"• **What you can try:**\n{info['what_to_try']}\n\n"
        f"• **When to contact support:** {info['contact_support']}"
    )


def match_faq(query_text):
    """
    Searches SQL FAQ database using token overlap, keyword matching, and normalized text.
    Returns (matched_faq, score).
    """
    if not query_text or len(query_text.strip()) < 3:
        return None, 0.0

    query_tokens = set(re.findall(r'\b[a-z0-9]{3,}\b', query_text.lower()))
    # Remove common conversational stop words
    stop_words = {'how', 'what', 'why', 'can', 'does', 'the', 'and', 'for', 'with', 'from', 'about', 'your', 'this', 'that', 'where'}
    meaningful_tokens = query_tokens - stop_words
    if not meaningful_tokens:
        meaningful_tokens = query_tokens

    active_faqs = FAQ.objects.filter(is_active=True)
    best_faq = None
    best_score = 0.0

    for faq in active_faqs:
        score = 0.0
        question_lower = faq.question.lower()
        keywords_lower = faq.keywords.lower() if faq.keywords else ""
        answer_lower = faq.answer.lower()

        # Exact substring match bonus
        if query_text.strip().lower() in question_lower:
            score += 2.0

        for token in meaningful_tokens:
            if token in question_lower:
                score += 1.0
            if token in keywords_lower:
                score += 0.8
            if token in answer_lower:
                score += 0.3

        normalized_score = score / (len(meaningful_tokens) + 1)
        if normalized_score > best_score:
            best_score = normalized_score
            best_faq = faq

    return best_faq, best_score


def process_user_message(user_message, conversation_id, user=None, session_id=None, previous_state=None):
    """
    Main assistant reasoning pipeline:
    1. Check for ticket creation confirmation.
    2. Check for error code explanations.
    3. Match against SQL FAQ knowledge base.
    4. If confidence is low, offer ticket escalation.
    5. Persist turn to MongoDB.
    """
    clean_msg = user_message.strip()
    msg_lower = clean_msg.lower()

    # 1. Check if user is confirming ticket creation
    ticket_confirm_triggers = ['yes', 'yes please', 'open ticket', 'create ticket', 'confirm ticket', 'please open a ticket', 'yes create ticket']
    is_confirming_ticket = any(trigger == msg_lower or msg_lower.startswith(trigger) for trigger in ticket_confirm_triggers)

    if (previous_state == 'ticket_offered' or is_confirming_ticket) and ('ticket' in msg_lower or is_confirming_ticket):
        subject = f"Chat Escalation: {clean_msg[:50]}" if len(clean_msg) > 10 else "Chat Escalation Request"
        description = f"User initiated ticket via Chatbot Assistant.\nRecent message: {clean_msg}\nConversation ID: {conversation_id}"
        
        ticket = SupportTicket.objects.create(
            user=user if user and user.is_authenticated else None,
            guest_email=user.email if user and user.is_authenticated and user.email else "guest@streamflix.local",
            subject=subject,
            description=description,
            category='General Inquiry',
            priority='Medium',
            source='Chatbot Assistant'
        )

        response_text = (
            f"✅ **Support Ticket Created!**\n\n"
            f"Your reference number is **{ticket.reference_number}**.\n\n"
            f"Our technical support team has received your inquiry. You can review and track your ticket status anytime on our [Support Desk](/support/).\n\n"
            f"Is there anything else I can help you with today?"
        )

        log_chat_message(
            conversation_id=conversation_id,
            message_role="user",
            message_text=clean_msg,
            user_id=user.id if user and user.is_authenticated else None,
            anonymous_session_id=session_id,
            response_type="ticket_created",
            support_ticket_reference=ticket.reference_number
        )
        log_chat_message(
            conversation_id=conversation_id,
            message_role="assistant",
            message_text=response_text,
            user_id=user.id if user and user.is_authenticated else None,
            anonymous_session_id=session_id,
            response_type="ticket_created",
            support_ticket_reference=ticket.reference_number
        )

        return {
            "reply": response_text,
            "type": "ticket_created",
            "ticket_ref": ticket.reference_number,
            "ticket_url": f"/support/ticket/{ticket.reference_number}/",
            "state": "resolved"
        }

    # 2. Check for Error Codes (400, 401, 403, 404, 429, 460, 500, 503)
    error_code = detect_error_code(clean_msg)
    if error_code:
        explanation = format_error_explanation(error_code)
        response_text = (
            f"Here is diagnostic information regarding **Error {error_code}**:\n\n"
            f"{explanation}\n\n"
            f"Would you like me to open a support ticket for this issue? Reply 'Yes' or click the button below."
        )

        log_chat_message(
            conversation_id=conversation_id,
            message_role="user",
            message_text=clean_msg,
            user_id=user.id if user and user.is_authenticated else None,
            anonymous_session_id=session_id,
            detected_error_code=error_code,
            response_type="error_explanation"
        )
        log_chat_message(
            conversation_id=conversation_id,
            message_role="assistant",
            message_text=response_text,
            user_id=user.id if user and user.is_authenticated else None,
            anonymous_session_id=session_id,
            detected_error_code=error_code,
            response_type="error_explanation"
        )

        return {
            "reply": response_text,
            "type": "error_explanation",
            "error_code": error_code,
            "ticket_offer": True,
            "state": "ticket_offered"
        }

    # 3. Match against SQL FAQ knowledge base
    matched_faq, score = match_faq(clean_msg)

    if matched_faq and score >= 0.45:
        response_text = (
            f"**{matched_faq.question}**\n\n"
            f"{matched_faq.answer}\n\n"
            f"*(Reference: FAQ #{matched_faq.id} - {matched_faq.category})*"
        )

        log_chat_message(
            conversation_id=conversation_id,
            message_role="user",
            message_text=clean_msg,
            user_id=user.id if user and user.is_authenticated else None,
            anonymous_session_id=session_id,
            matched_faq_id=matched_faq.id,
            response_type="faq_answer"
        )
        log_chat_message(
            conversation_id=conversation_id,
            message_role="assistant",
            message_text=response_text,
            user_id=user.id if user and user.is_authenticated else None,
            anonymous_session_id=session_id,
            matched_faq_id=matched_faq.id,
            response_type="faq_answer"
        )

        return {
            "reply": response_text,
            "type": "faq_answer",
            "faq_id": matched_faq.id,
            "category": matched_faq.category,
            "ticket_offer": False,
            "state": "answered"
        }

    # 4. Unknown question or low confidence: Offer Support Ticket escalation
    response_text = (
        "I couldn't find a direct answer to your question in our knowledge base.\n\n"
        "Would you like me to open a support ticket with our engineering and support team? "
        "Just reply **'Yes'** or click **'Create Support Ticket'** below."
    )

    log_chat_message(
        conversation_id=conversation_id,
        message_role="user",
        message_text=clean_msg,
        user_id=user.id if user and user.is_authenticated else None,
        anonymous_session_id=session_id,
        response_type="ticket_offer"
    )
    log_chat_message(
        conversation_id=conversation_id,
        message_role="assistant",
        message_text=response_text,
        user_id=user.id if user and user.is_authenticated else None,
        anonymous_session_id=session_id,
        response_type="ticket_offer"
    )

    return {
        "reply": response_text,
        "type": "ticket_offer",
        "ticket_offer": True,
        "state": "ticket_offered"
    }
