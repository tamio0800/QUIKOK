from django.urls import path

from . import views

urlpatterns = [
    
    path('<str:user_url>/', views.chat, name='chat'),
]
