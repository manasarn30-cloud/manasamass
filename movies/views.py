import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.db.models import Q
from movies.models import Movie, MyList
from movies.tmdb import TMDBClient

logger = logging.getLogger('streamflix')
tmdb_client = TMDBClient()


def _get_user_saved_movie_ids(user):
    """Helper to return set of saved movie IDs for the authenticated user."""
    if user.is_authenticated:
        return set(user.saved_movies.values_list('movie_id', flat=True))
    return set()


def home_view(request):
    """
    Cinematic streaming dashboard:
    - Hero banner with featured content
    - Horizontal rows: Trending, Popular, Sci-Fi, Action, Thriller, Drama
    """
    saved_ids = _get_user_saved_movie_ids(request.user)

    # Hero movie: prefer Interstellar or highest-rated featured film
    hero_movie = tmdb_client.get_featured_hero()

    # Category rows
    trending_movies = tmdb_client.get_trending()
    popular_movies = tmdb_client.get_popular()
    scifi_movies = tmdb_client.get_by_genre('Sci-Fi')
    action_movies = tmdb_client.get_by_genre('Action')
    thriller_movies = tmdb_client.get_by_genre('Thriller')
    drama_movies = tmdb_client.get_by_genre('Drama')

    context = {
        'hero_movie': hero_movie,
        'trending_movies': trending_movies,
        'popular_movies': popular_movies,
        'scifi_movies': scifi_movies,
        'action_movies': action_movies,
        'thriller_movies': thriller_movies,
        'drama_movies': drama_movies,
        'saved_ids': saved_ids,
    }
    return render(request, 'movies/home.html', context)


def discover_view(request):
    """
    Search and movie discovery catalog:
    Supports query parameter search, genre filtering chips, and sorting.
    """
    query = request.GET.get('q', '').strip()
    selected_genre = request.GET.get('genre', '').strip()
    sort_by = request.GET.get('sort', 'rating_desc')

    # Query SQL first
    qs = Movie.objects.all()

    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(overview__icontains=query))

    if selected_genre and selected_genre != 'All':
        qs = qs.filter(genre__icontains=selected_genre)

    # Sorting
    if sort_by == 'rating_desc':
        qs = qs.order_by('-rating')
    elif sort_by == 'rating_asc':
        qs = qs.order_by('rating')
    elif sort_by == 'release_desc':
        qs = qs.order_by('-release_date')
    elif sort_by == 'title_asc':
        qs = qs.order_by('title')
    else:
        qs = qs.order_by('-rating')

    movies_list = list(qs)

    # If SQL query returns nothing and query exists, attempt TMDB search
    if not movies_list and query:
        movies_list = tmdb_client.search(query)

    genres = ['All', 'Action', 'Sci-Fi', 'Drama', 'Comedy', 'Thriller', 'Adventure', 'Crime']
    saved_ids = _get_user_saved_movie_ids(request.user)

    context = {
        'movies': movies_list,
        'query': query,
        'selected_genre': selected_genre or 'All',
        'sort_by': sort_by,
        'genres': genres,
        'total_results': len(movies_list),
        'saved_ids': saved_ids,
    }

    # Handle AJAX fetch if requested
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'movies/partials/movie_grid.html', context)

    return render(request, 'movies/discover.html', context)


def movie_detail_view(request, movie_id):
    """
    Cinematic movie details view with synopsis, metadata, trailer embed,
    and recommended similar films.
    """
    movie = None
    try:
        movie = Movie.objects.get(pk=movie_id)
    except (Movie.DoesNotExist, ValueError):
        # Check by tmdb_id or fallback
        movie = tmdb_client.get_movie_detail(movie_id)

    if not movie:
        raise Http404("The requested movie could not be found.")

    is_saved = False
    saved_ids = _get_user_saved_movie_ids(request.user)
    if isinstance(movie, Movie):
        is_saved = movie.id in saved_ids
    elif isinstance(movie, dict):
        is_saved = movie.get('id') in saved_ids or movie.get('tmdb_id') in saved_ids

    # Extract YouTube video key for clean embed if available
    trailer_key = ""
    trailer_url = getattr(movie, 'trailer_url', '') if isinstance(movie, Movie) else movie.get('trailer_url', '')
    if 'v=' in trailer_url:
        trailer_key = trailer_url.split('v=')[-1].split('&')[0]
    elif 'youtu.be/' in trailer_url:
        trailer_key = trailer_url.split('youtu.be/')[-1].split('?')[0]

    # Similar movies based on genre
    genre_hint = getattr(movie, 'genre', '') if isinstance(movie, Movie) else movie.get('genre', '')
    primary_genre = genre_hint.split(',')[0].strip() if genre_hint else 'Action'
    similar_movies = Movie.objects.filter(genre__icontains=primary_genre).exclude(
        pk=getattr(movie, 'id', None)
    )[:6]

    context = {
        'movie': movie,
        'is_saved': is_saved,
        'trailer_key': trailer_key,
        'similar_movies': similar_movies,
        'saved_ids': saved_ids,
    }
    return render(request, 'movies/detail.html', context)


@login_required
def my_list_view(request):
    """Displays the authenticated user's private saved movies."""
    saved_items = request.user.saved_movies.select_related('movie').all()
    movies = [item.movie for item in saved_items]
    saved_ids = {m.id for m in movies}

    context = {
        'movies': movies,
        'total_saved': len(movies),
        'saved_ids': saved_ids,
    }
    return render(request, 'movies/my_list.html', context)


@login_required
@require_POST
def toggle_my_list_view(request, movie_id):
    """
    AJAX endpoint to add/remove a movie from user's personal list.
    Returns JSON response with updated list state.
    """
    movie = get_object_or_404(Movie, pk=movie_id)
    saved_entry = MyList.objects.filter(user=request.user, movie=movie).first()

    if saved_entry:
        saved_entry.delete()
        in_list = False
        message = f"Removed '{movie.title}' from My List."
    else:
        MyList.objects.create(user=request.user, movie=movie)
        in_list = True
        message = f"Added '{movie.title}' to My List."

    new_count = request.user.saved_movies.count()

    return JsonResponse({
        'success': True,
        'in_list': in_list,
        'movie_id': movie.id,
        'total_count': new_count,
        'message': message,
    })
