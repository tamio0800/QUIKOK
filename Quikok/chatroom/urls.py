from django.urls import path

from . import views

urlpatterns = [
    path('check_or_create_chatroom/',views.checkOrCreateChatroom),
    path('<str:user_url>/', views.chat, name='chat'),
]
