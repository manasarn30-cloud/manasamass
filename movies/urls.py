from django.urls import path
from movies import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('discover/', views.discover_view, name='discover'),
    path('movie/<int:movie_id>/', views.movie_detail_view, name='movie_detail'),
    path('my-list/', views.my_list_view, name='my_list'),
    path('my-list/toggle/<int:movie_id>/', views.toggle_my_list_view, name='toggle_my_list'),
]
