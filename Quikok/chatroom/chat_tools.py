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
        # 依據要回傳給前端的字典格式建立空的self字典
        # response_msg字典裏面又包含兩層字典
        # 因為感覺之後會直接叫裡面的字典來修改、再更新較外層的字典,
        # 因此先將這幾層字典都設 self (尚不清楚是否可以這樣做XD)
        response_msg_key = ['chatroomID','chatUnreadMessageQty', 'chatUserID', 'chatUserType',
                        'chatUserName', 'chatUserPath', 'messageInfo']
        self.response_msg = dict()
        for key in response_msg_key:
            self.response_msg[key] = None
        a_message_info_dict_keys = ['userID','messageType','messageText','bookingRelatedMessage', 
                                    'systemCode', 'messageCreateTime']
        self.message_info =dict()
        for key in a_message_info_dict_keys:
            self.message_info[key] = None  
        booking_related_message_key = ['bookingID', 'bookingLeesonID', 'bookingStatus',
                                        'bookingDate', 'bookingTime', 'bookingUpdateTime']
        self.booking_related_message_dict = dict()
        for key in booking_related_message_key:
            self.booking_related_message[key] = None
        self.message_info['bookingRelatedMessage'] = self.booking_related_message_dict
        # 因為booking資訊是在message裡面，先更新message字典再把message字典更新到info大字典
        self.response_msg['messageInfo'] = self.a_message_dict

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
        parent_authID = -1 #暫時未使用因此設 -1
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
    def chat_main_content(self, **kwargs):
        # 目前先設定0~100之後這個變數可以給前端傳
        # 希望可以達到假設user滑到頂一次給100之類的效果(前端告訴後端user是第幾次滑到頂)
        #number_of_history_start = 0
        #number_of_history_end = 100
        #chat_messages = Messages.objects.filter(group=room_id).order_by("timestamp")[number_of_history_start:number_of_history_end] 
        
        # 首先篩選出所有這個人的聊天室
        user_type = kwargs['user_type']
        if user_type == 'teacher':
            #user_teacher = teacher_profile.objects.filter(username= kwargs['userID'])
            user_chatrooms_with_user = chatroom_info_user2user.objects.filter(teacher_auth_id=kwargs['userID'])
        elif user_type == 'student':
            #user_student = student_profile.objects.filter(username= kwargs['userID'])
            user_chatrooms_with_user = chatroom_info_user2user.objects.filter(student_auth_id=kwargs['userID'])
        
        room_queryset=chatroom_info_user2user.objects.filter(Q(student_auth_id=kwargs['userID'])|Q(teacher_auth_id=kwargs['userID'])).order_by("-date")
        
        # 如果有資料的前提..
        # 包成可以回傳給前端的格式
        for a_chatroom in room_queryset:
            chatroomID = a_chatroom.id
            if user_type == 'teacher':
                chatUserID = a_chatroom.student_auth_id
                chat_user = student_profile.objects.filter(auth_id = a_chatroom.student_auth_id).first()
                chatUserType = 'student'
            elif user_type == 'student':
                chatUserID = a_chatroom.teacher_auth_id
                chat_user = student_profile.objects.filter(auth_id = a_chatroom.teacher_auth_id).first()
                chatUserType = 'teacher'
            
            chatUserPath = chat_user.thumbnail_dir
            chatUserName = chat_user.nickname
            ### 紀錄一下最外層目前已有這些資訊 response_value = [chatroomID, chatUserID, chatUserType, chatUserName]
            # 接下來是 chatUnreadMessageQty
            # 歷史訊息的id = roomid,且發送者不是 user, 且未讀 = 0
            chat_history_obj = chat_history_user2user.objects.filter(Q(chatroom_info_user2user_id=chatroomID)&Q(is_read = 0)& ~Q(who_is_sender = kwargs['userID']))
            chatUnreadMessageQty = len(chat_history_obj)
            
            # messageInfo 每一則訊息的資訊
            # messageType: 訊息類別(0:一般文字, 1:系統訊息, 2:預約方塊)
            all_messages = chat_history_user2user.objects.filter(chatroom_info_user2user_id=chatroomID).order_by("timestamp")
            for a_message in all_messages:
                msg_sender = a_message.who_is_sender
                if msg_sender == 
                
        
    def chat_customer_service_messeage(self):
        pass
    # 偵測是否有系統該發送訊息到room情況
    # 以及發送訊息
    def system_2user(self):
        pass
