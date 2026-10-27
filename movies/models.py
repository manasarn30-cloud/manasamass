from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    """
    SQL model storing movie metadata.
    Can be populated from TMDB API or seed fallback data.
    """
    tmdb_id = models.IntegerField(null=True, blank=True, db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=500, blank=True)
    backdrop_path = models.CharField(max_length=500, blank=True)
    release_date = models.CharField(max_length=50, blank=True)
    rating = models.FloatField(default=0.0)
    vote_count = models.IntegerField(default=0)
    genre = models.CharField(max_length=150, blank=True, db_index=True)
    runtime = models.IntegerField(null=True, blank=True, help_text="Runtime in minutes")
    trailer_url = models.URLField(max_length=500, blank=True)
    
    # Categorization flags for featured rows
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-created_at']

    def __str__(self):
        return self.title

    @property
    def poster_url(self):
        if self.poster_path:
            if self.poster_path.startswith(('http://', 'https://')):
                return self.poster_path
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return "/static/images/poster_placeholder.png"

    @property
    def backdrop_url(self):
        if self.backdrop_path:
            if self.backdrop_path.startswith(('http://', 'https://')):
                return self.backdrop_path
            return f"https://image.tmdb.org/t/p/original{self.backdrop_path}"
        return "/static/images/backdrop_placeholder.png"

    @property
    def release_year(self):
        if self.release_date and len(self.release_date) >= 4:
            return self.release_date[:4]
        return ""


class MyList(models.Model):
    """
    User-specific saved movie list.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='saved_in_lists')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
