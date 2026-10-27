"""
URL configuration for StreamFlix project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('movies.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('support.urls')),
    path('', include('monitoring.urls')),
]

# Custom HTTP error handlers
handler400 = 'monitoring.handlers.bad_request_view'
handler403 = 'monitoring.handlers.permission_denied_view'
handler404 = 'monitoring.handlers.page_not_found_view'
handler500 = 'monitoring.handlers.server_error_view'
