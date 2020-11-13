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
        chatroom_key = ['chatID','chatUnreadMessageQty', 'chatUserID', 'chatUserType',
                        'chatUserName', 'chatUserPath', 'messageInfo']
        self.chat_content = dict()
        for key in chatroom_key:
            self.chat_content[key] = None
            
        booking_related_message_key = ['bookingID', 'bookingLeesonID', 'bookingStatus',
                                        'bookingDate', 'bookingTime', 'bookingUpdateTime']
        self.booking_related_message_dict = dict()
        for key in booking_related_message_key:
            self.booking_related_message[key] = None
        a_message_info_dict_keys = ['userID','messageType','messageText','bookingRelatedMessage', 
                                    'systemCode', 'messageCreateTime']
        self.a_message_dict =dict()
        for key in a_message_info_dict_keys:
            self.a_message_dict[key] = None
        self.a_message_dict['bookingRelatedMessage'] = self.booking_related_message_dict

        self.chat_content['messageInfo'] = self.a_message_dict

    # 建立一些error回應
    def response_to_frontend(check_result):
        if check_result == 1:
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Query failed'

    # 建立聊天室
    def check_and_create_chat_room(self,**kwargs):
        student_authID = kwargs['userID']
        teacher_authID = kwargs['chatUserID']
        parent_authID = -1 #暫時未使用
        chatroom_type = 'teacher2student' # 暫時只有這種
        try:
            chatroom = chatroom_info_user2user.objects.filter(Q(student_auth_id=student_authID)&Q(teacher_auth_id=teacher_authID))
            if len(chatroom) == 0 :
                new_chatroom = chatroom_info_user2user.objects.create(student_auth_id=student_authID,
                teacher_auth_id=teacher_authID, parent_auth_id = parent_authID,
                chatroom_type = chatroom_type)
                print('create new chatroom')
                self.status = 'success'
                self.errCode = None
                self.errMsg = None
                self.data = list()
                data = {'data' : new_chatroom.id}
                self.data.append(data)
                return (self.status, self.errCode, self.errMsg, self.data)               
            else:
                print('their chatroom already exist')
                self.status = 'success'
                self.errCode = None
                self.errMsg = None
                self.data = list()
                data = {'data' : chatroom.id}
                self.data.append(data)
                return (self.status, self.errCode, self.errMsg, self.data)
        except Exception as e:
            print(e)
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Querying Data Failed.'

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
