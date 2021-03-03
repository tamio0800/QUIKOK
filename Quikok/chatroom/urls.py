from django.urls import path

from . import views

urlpatterns = [
    path('checkOrCreateChatroom/',views.check_if_chatroom_exist),
    path('checkSystemChatroom/',views.check_system_chatroom),
    path('contentAndHistoryOfChatroom/',views.chatroom_content),
    path('contentAndHistoryOfSystemChatroom/',views.system_chatroom_content),
    path('updateUser2UserIsRead/',views.update_user2user_chatroom_msg_is_read),
     
    
    #path('<str:user_url>/', views.chat, name='chat'),
]
