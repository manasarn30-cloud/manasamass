from django.urls import path
from support import views

urlpatterns = [
    path('faq/', views.faq_view, name='faq'),
    path('support/', views.support_ticket_list_view, name='support'),
    path('support/ticket/new/', views.create_ticket_view, name='create_ticket'),
    path('support/ticket/<str:reference_number>/', views.support_ticket_detail_view, name='ticket_detail'),
    path('api/chatbot/', views.chatbot_api_view, name='chatbot_api'),
    path('api/chatbot/feedback/', views.chatbot_feedback_api_view, name='chatbot_feedback'),
]
