from django.shortcuts import render


def bad_request_view(request, exception=None):
    """Custom 400 error handler."""
    return render(request, 'errors/400.html', {'error_code': 400}, status=400)


def permission_denied_view(request, exception=None):
    """Custom 403 error handler."""
    return render(request, 'errors/403.html', {'error_code': 403}, status=403)


def page_not_found_view(request, exception=None):
    """Custom 404 error handler."""
    return render(request, 'errors/404.html', {'error_code': 404}, status=404)


def server_error_view(request):
    """Custom 500 error handler."""
    return render(request, 'errors/500.html', {'error_code': 500}, status=500)
