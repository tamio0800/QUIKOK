from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from .models import *
from account.models import student_profile, teacher_profile
from datetime import datetime

class chat_room_manager:
    def __init__(self):
        self.status = None
        self.errCode = None
        self.errMsg = None
        self.data = None
        # 依據要回傳給前端的字典格式建立空的self字典
        # response_msg字典裏面又包含兩層字典
        # 因為感覺之後會直接叫裡面的字典來修改、再更新較外層的字典,
        # 因此先將這幾層字典都設 self 
        response_msg_key = ['chatroomID','chatUnreadMessageQty', 'chatUserID', 'chatUserType',
                        'chatUserName', 'chatUserPath', 'messageInfo']
        self.response_msg_key = ['chatroomID','chatUnreadMessageQty', 'chatUserID', 'chatUserType',
                        'chatUserName', 'chatUserPath', 'messageInfo']
        
        self.response_msg = dict()
        for key in response_msg_key:
            self.response_msg[key] = None
        a_message_info_dict_keys = ['userID','messageType','messageText','bookingRelatedMessage', 
                                    'systemCode', 'messageCreateTime']
        self.message_info_group = list()
        self.a_message_info = dict()
        for key in a_message_info_dict_keys:
            self.a_message_info[key] = None  
        # 預約message 的keys的keys
        booking_related_message_key = ['bookingID', 'bookingLeesonID', 'bookingStatus',
                                      'bookingDate', 'bookingTime', 'bookingUpdateTime']
        self.booking_related_message_dict = dict()
        for key in booking_related_message_key:
            self.booking_related_message_dict[key] = None
        #self.message_info['bookingRelatedMessage'] = self.booking_related_message_dict
        # 註解掉因為現在回傳用不到這個字典
        # 因為booking資訊是在message裡面，先更新message字典再把message字典更新到info大字典
        self.response_msg['messageInfo'] = self.message_info_group

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
                self.data = {'chatID' : new_chatroom.id}
                return (self.status, self.errCode, self.errMsg, self.data)               
            elif len(chatroom) == 1 :
                print('their chatroom already exist')
                self.status = 'success'
                self.errCode = None
                self.errMsg = None
                self.data = {'chatID' : chatroom[0].id}
                return (self.status, self.errCode, self.errMsg, self.data)
            else:
                print('something wrong...find multi chatrooms')
        except Exception as e:
            print(e)
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Querying Data Failed.'
            return (self.status, self.errCode, self.errMsg, self.data)

    # 調出主對話框全部內容
    # kwargs: userID, user_type
    def chat_main_content(self, **kwargs):
        # 目前先設定0~100之後這個變數可以給前端傳
        # 希望可以達到假設user滑到頂一次給100之類的效果(前端告訴後端user是第幾次滑到頂)
        #number_of_history_start = 0
        #number_of_history_end = 100
        #chat_messages = Messages.objects.filter(group=room_id).order_by("timestamp")[number_of_history_start:number_of_history_end] 
        self.data = list()
        try:
            # 首先篩選出所有這個人的聊天室
            user_type = kwargs['user_type']
            if user_type == 'teacher':
                #user_teacher = teacher_profile.objects.filter(username= kwargs['userID'])
                user_chatrooms_with_user = chatroom_info_user2user.objects.filter(teacher_auth_id=kwargs['userID'])
            elif user_type == 'student':
                #user_student = student_profile.objects.filter(username= kwargs['userID'])
                user_chatrooms_with_user = chatroom_info_user2user.objects.filter(student_auth_id=kwargs['userID'])
            else: # 之後會有其他種type
                pass
            room_queryset= chatroom_info_user2user.objects.filter(Q(student_auth_id=kwargs['userID'])|Q(teacher_auth_id=kwargs['userID'])).order_by("created_time")
            print('使用者有這些聊天室')
            print(room_queryset)
            # 如果有資料的前提..
            # 包成可以回傳給前端的格式
            if len(room_queryset) >0:
                response_data = list()
                for a_chatroom in room_queryset:
                    a_chatroom_info = dict()
                    for key in self.response_msg_key:
                        a_chatroom_info[key] = None
                    chatroomID = a_chatroom.id
                    if user_type == 'teacher':
                        chatUserID = a_chatroom.student_auth_id
                        chat_user = student_profile.objects.filter(auth_id = chatUserID).first()

                        chatUserType = 'student'
                    elif user_type == 'student':
                        chatUserID = a_chatroom.teacher_auth_id
                        chat_user = teacher_profile.objects.filter(auth_id = chatUserID).first()
                        chatUserType = 'teacher'
                    else: # 將來可能有其他類別
                        pass
                    # 對方可能會沒有大頭貼
                    if len(chat_user.thumbnail_dir) > 0:
                        print(chat_user.thumbnail_dir)
                        chatUserPath = chat_user.thumbnail_dir
                    else:
                        chatUserPath = ''
                    chatUserName = chat_user.nickname
                     # chatUnreadMessageQty 歷史訊息的id = roomid,且發送者不是 user, 且未讀 = 0
                    chat_history_obj = chat_history_user2user.objects.filter(Q(chatroom_info_user2user_id=chatroomID)&Q(is_read = 0)& ~Q(who_is_sender = kwargs['userID']))
                    chatUnreadMessageQty = len(chat_history_obj)
                    update_response_msg = {'chatroomID':chatroomID,'chatUnreadMessageQty':chatUnreadMessageQty,
                    'chatUserID' : chatUserID, 'chatUserType': chatUserType ,
                                'chatUserName' : chatUserName, 'chatUserPath' : chatUserPath}
                    a_chatroom_info.update(update_response_msg)
                # messageInfo 每一則訊息的資訊
                # messageType: 訊息類別(0:一般文字, 1:系統訊息, 2:預約方塊)
                    all_messages = chat_history_user2user.objects.filter(chatroom_info_user2user_id=chatroomID).order_by("created_time")
                    if len(all_messages) > 0:
                        message_info_group = list()
                        for a_message in all_messages:
                            temp_info = dict()
                            temp_info['senderID'] = a_message.who_is_sender
                            temp_info['messageType'] = a_message.message_type
                            temp_info['messegText'] = a_message.message
                            temp_info['messageCreateTime'] = a_message.created_time
                            if a_message.message_type == 1:
                                temp_info['systemCode'] = 0
                            else:
                                temp_info['systemCode'] = -1
                            message_info_group.append(temp_info)
                    else:
                        #print('本聊天室沒有任何訊息')
                        message_info_group = list()

                    a_chatroom_info['messageInfo'] = message_info_group 
                    response_data.append(a_chatroom_info)
                #print(response_data)
                self.status = 'success'
                self.data = response_data
            else: # 尚未建立任何聊天室
                self.status = 'success'
            return (self.status, self.errCode, self.errMsg, self.data)
        
        except Exception as e:
            print(e)
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Querying Data Failed.'
            return (self.status, self.errCode, self.errMsg, self.data)

        
        
    def chat_customer_service_messeage(self):
        pass
    # 偵測是否有系統該發送訊息到room情況
    # 以及發送訊息
    def system_2user(self):
        pass

class websocket_manager:
    def chat_storge(self, **kwargs):
        chatroom_id = kwargs['chatID']
        sender = kwargs['userID']
        message = kwargs['message']
        messageType = kwargs['messageType']

        try:
            chatroom_info = chatroom_info_user2user.objects.filter(id = chatroom_id).first()
            if sender == chatroom_info.student_auth_id:
                # 發送者是學生
                teacher_auth_id = chatroom_info.teacher_auth_id
                student_auth_id = sender
            elif sender == chatroom_info.teacher_auth_id:
                teacher_auth_id = sender
                student_auth_id= chatroom_info.student_auth_id
            parent_auth_id = -1 # 目前先給-1

            chat_history_user2user.objects.create(
                chatroom_info_user2user_id= chatroom_id,
                teacher_auth_id =teacher_auth_id,
                student_auth_id= student_auth_id,
                parent_auth_id =parent_auth_id,
                message = message,
                message_type= messageType,
                who_is_sender= sender,
                is_read= 0,
                created_time=datetime.now()).save()
        
        except Exception as e:
            print(e)
            
    