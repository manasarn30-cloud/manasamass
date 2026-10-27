from django.contrib import admin
from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorite_genre', 'created_at')
    search_fields = ('user__username', 'user__email', 'favorite_genre')
