import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from accounts.forms import SignUpForm, LoginForm, ProfileUpdateForm

logger = logging.getLogger('streamflix')


def signup_view(request):
    """Handles new user registration."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create user safely with hashed password
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            # Log the user in directly
            login(request, user)
            logger.info(f"New user registered: {username} (ID: {user.id})")
            messages.success(request, f"Welcome to StreamFlix, {username}! Your account has been created.")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """Handles user authentication with username or email."""
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email'].strip()
            password = form.cleaned_data['password']

            # Check if input is email or username
            user_obj = None
            if '@' in username_or_email:
                try:
                    matched_user = User.objects.filter(email__iexact=username_or_email).first()
                    if matched_user:
                        user_obj = authenticate(request, username=matched_user.username, password=password)
                except Exception as e:
                    logger.warning(f"Error checking email login: {e}")
            else:
                user_obj = authenticate(request, username=username_or_email, password=password)

            if user_obj is not None:
                if user_obj.is_active:
                    login(request, user_obj)
                    logger.info(f"User logged in: {user_obj.username}")
                    messages.success(request, f"Welcome back, {user_obj.username}!")
                    # Prevent open redirect vulnerability
                    if next_url.startswith('/'):
                        return redirect(next_url)
                    return redirect('home')
                else:
                    messages.error(request, "This account is inactive. Please contact support.")
            else:
                logger.warning(f"Failed login attempt for identifier: {username_or_email}")
                messages.error(request, "Invalid username/email or password. Please try again.")
        else:
            messages.error(request, "Please fill in all required fields.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


@require_POST
def logout_view(request):
    """
    Handles user logout via secure HTTP POST request.
    Prevents CSRF and unintended GET-based logouts.
    """
    username = request.user.username if request.user.is_authenticated else "anonymous"
    logout(request)
    logger.info(f"User logged out: {username}")
    messages.info(request, "You have been successfully logged out. See you soon!")
    return redirect('home')


@login_required
def profile_view(request):
    """Displays user profile, account statistics, and allows updating preferences."""
    profile = request.user.profile
    saved_movies_count = request.user.saved_movies.count()
    tickets_count = request.user.support_tickets.count()

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile preferences have been updated.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'saved_movies_count': saved_movies_count,
        'tickets_count': tickets_count,
    }
    return render(request, 'accounts/profile.html', context)
