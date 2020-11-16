from django.urls import path

from . import views

urlpatterns = [
    path('checkOrCreateChatroom/',views.check_if_chatroom_exist),
    path('contentAndHistoryOfChatroom/',views.chatroom_content),
    path('<str:user_url>/', views.chat, name='chat'),
]
