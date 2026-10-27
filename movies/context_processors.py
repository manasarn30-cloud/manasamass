from django.conf import settings
from datetime import datetime


def movie_context(request):
    """
    Context processor making user list count and platform settings available to all templates.
    """
    my_list_count = 0
    if request.user.is_authenticated:
        try:
            my_list_count = request.user.saved_movies.count()
        except Exception:
            my_list_count = 0

    tmdb_configured = bool(getattr(settings, 'TMDB_API_KEY', '').strip())

    return {
        'site_name': 'StreamFlix',
        'my_list_count': my_list_count,
        'tmdb_configured': tmdb_configured,
        'tmdb_mode': 'Live TMDB API' if tmdb_configured else 'Curated Fallback Catalog',
        'current_year': datetime.now().year,
    }
