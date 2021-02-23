from django.urls import path

from . import views

urlpatterns = [
    path('checkOrCreateChatroom/',views.check_if_chatroom_exist),
    path('contentAndHistoryOfChatroom/',views.chatroom_content),
    path('updateUser2UserIsRead/',views.update_user2user_chatroom_msg_is_read),
    path('checkSystemChatroom/',views.check_system_chatroom), 
    
    #path('<str:user_url>/', views.chat, name='chat'),
]
