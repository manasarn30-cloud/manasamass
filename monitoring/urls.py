from django.urls import path
from monitoring import views

urlpatterns = [
    path('health/', views.health_check_view, name='health_check'),
    path('test-error/<int:code>/', views.test_error_view, name='test_error'),
]
