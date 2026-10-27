import time
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.conf import settings
from support.mongo import check_mongo_health
from movies.tmdb import TMDBClient

tmdb_client = TMDBClient()


def health_check_view(request):
    """
    Production health-check endpoint (/health/).
    Returns machine-readable JSON status of platform services:
    - Django application runtime
    - SQL database connectivity
    - MongoDB persistence availability
    - TMDB API configuration status
    """
    start_time = time.time()
    checks = {}
    is_healthy = True

    # 1. Django core
    checks['django'] = 'healthy'

    # 2. SQL Database Check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row and row[0] == 1:
                checks['sql_database'] = {
                    'status': 'connected',
                    'engine': connection.settings_dict.get('ENGINE', 'sqlite3').split('.')[-1]
                }
            else:
                checks['sql_database'] = {'status': 'unexpected_response'}
                is_healthy = False
    except Exception as e:
        checks['sql_database'] = {'status': 'disconnected', 'error': str(e.__class__.__name__)}
        is_healthy = False

    # 3. MongoDB Persistence Check
    mongo_ok, mongo_msg = check_mongo_health()
    checks['mongodb'] = {
        'status': mongo_msg,
        'role': 'persistent_chat_logs_and_feedback',
        'connected': mongo_ok
    }

    # 4. TMDB Third-party API
    checks['tmdb_api'] = {
        'status': 'configured' if tmdb_client.is_configured else 'curated_fallback_mode',
        'timeout_seconds': getattr(settings, 'TMDB_TIMEOUT', 5.0)
    }

    duration_ms = round((time.time() - start_time) * 1000, 2)
    response_data = {
        'status': 'healthy' if is_healthy else 'degraded',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'latency_ms': duration_ms,
        'checks': checks,
    }

    status_code = 200 if is_healthy else 503
    return JsonResponse(response_data, status=status_code)


def test_error_view(request, code):
    """
    Safe diagnostic test view for demonstrating custom error pages.
    Accessible via /test-error/<code>/
    Supported codes: 400, 401, 403, 404, 429, 460, 500, 503
    """
    valid_codes = {400, 401, 403, 404, 429, 460, 500, 503}
    if code not in valid_codes:
        code = 404

    template_name = f"errors/{code}.html"
    context = {
        'error_code': code,
        'request_path': request.path,
    }
    return render(request, template_name, context, status=code)
