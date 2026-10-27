import time
import uuid
import logging

logger = logging.getLogger('streamflix')

# Parameters to mask in logs for privacy and security
SENSITIVE_KEYS = {
    'password', 'password1', 'password2', 'confirm_password',
    'secret', 'token', 'authorization', 'csrfmiddlewaretoken',
    'sessionid', 'api_key', 'credit_card', 'access_token'
}


def sanitize_dict(data):
    """Masks sensitive values in dictionary for safe logging."""
    if not isinstance(data, dict):
        return data
    sanitized = {}
    for key, value in data.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = '***REDACTED***'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        else:
            sanitized[key] = value
    return sanitized


class RequestLoggingMiddleware:
    """
    Middleware that records HTTP requests and responses.
    Logs method, path, status, duration, request_id, and handles errors safely.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())[:8]
        request.request_id = request_id
        start_time = time.time()

        # Capture client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

        try:
            response = self.get_response(request)
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"[{request_id}] {request.method} {request.path} FAILED with unhandled exception: {exc} | duration={duration_ms}ms | ip={ip}"
            )
            raise

        duration_ms = round((time.time() - start_time) * 1000, 2)
        response['X-Request-ID'] = request_id

        # Skip spamming logs on static asset requests if desired, but log all application endpoints
        if not request.path.startswith('/static/'):
            status_code = getattr(response, 'status_code', 200)
            log_level = logging.INFO
            if status_code >= 500:
                log_level = logging.ERROR
            elif status_code >= 400:
                log_level = logging.WARNING

            logger.log(
                log_level,
                f"[{request_id}] {request.method} {request.path} status={status_code} duration={duration_ms}ms ip={ip}"
            )

        return response
