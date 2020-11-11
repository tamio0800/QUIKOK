from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from .models import *
from account.models import student_profile, teacher_profile


class chat_room_manager:
    def __init__(self):
        self.status = None
        self.errCode = None
        self.errMsg = None
        self.data = None
    # 建立一些error回應
    def response_to_frontend(check_result):
        if check_result == 1:
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Token Unmatch'

    # 建立聊天室
    def create_chat_room(self,**kwargs):
        student_authID = kwargs['user1']
        teacher_authID = kwargs['user2']
        parent_authID = None #暫時未使用
        chatroom = chatroom_info_user2user.objects.filter(Q(student_auth_id=student_authID)&Q(teacher_auth_id=teacher_authID))
        if len(chatroom) == 0 :
            chatroom_info_user2user.objects.create(student_auth_id=student_authID,
            teacher_auth_id=teacher_authID, parent_auth_id = parent_authID)
            print('create new chatroom')
        else:
            print('their chatroom already exist')
            pass
        

    # 調出主對話框全部內容
    def chat_main_content(self, userID):
        # 目前先設定0~100之後這個變數可以給前端傳
        # 希望可以達到假設user滑到頂一次給100之類的效果(前端告訴後端user是第幾次滑到頂)
        number_of_history_start = 0
        number_of_history_end = 100
        chat_messages = Messages.objects.filter(group=room_id).order_by("timestamp")[number_of_history_start:number_of_history_end] 

        chatroom_ID = ''
        chat_with_userID = '' 
        chat_with_user_thumbnail = ''

        
    def chat_customer_service_messeage(self):
        pass
    # 偵測是否有系統該發送訊息到room情況
    # 以及發送訊息
    def system_2user(self):
        pass
