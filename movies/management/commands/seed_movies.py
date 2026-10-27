from django.core.management.base import BaseCommand
from movies.models import Movie
from movies.tmdb import FALLBACK_MOVIES


class Command(BaseCommand):
    help = 'Seeds initial curated movies into the SQL database.'

    def handle(self, *args, **options):
        count = 0
        for item in FALLBACK_MOVIES:
            movie, created = Movie.objects.update_or_create(
                title=item["title"],
                defaults={
                    "tmdb_id": item.get("tmdb_id"),
                    "overview": item.get("overview", ""),
                    "poster_path": item.get("poster_path", ""),
                    "backdrop_path": item.get("backdrop_path", ""),
                    "release_date": item.get("release_date", ""),
                    "rating": item.get("rating", 0.0),
                    "vote_count": item.get("vote_count", 0),
                    "genre": item.get("genre", ""),
                    "runtime": item.get("runtime"),
                    "trailer_url": item.get("trailer_url", ""),
                    "is_featured": item.get("is_featured", False),
                    "is_trending": item.get("is_trending", False),
                    "is_popular": item.get("is_popular", False),
                }
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} movies into the SQL database."))
