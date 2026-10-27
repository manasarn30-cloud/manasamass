from django.contrib import admin
from movies.models import Movie, MyList


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'genre', 'release_date', 'is_featured', 'is_trending', 'is_popular')
    list_filter = ('is_featured', 'is_trending', 'is_popular', 'genre')
    search_fields = ('title', 'overview', 'genre')
    ordering = ('-rating', 'title')


@admin.register(MyList)
class MyListAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'movie__title')
