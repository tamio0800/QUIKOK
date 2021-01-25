from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from .models import *
from account.models import student_profile, teacher_profile
from datetime import datetime
from .system_2user_layer import layer_info_maneger


class system_msg_producer:
    # 傳訊息代碼進來, 回應相對的資訊
    def wellcome_msg(self):
        pass
    def first_system_msg(self):
        pass
class chat_room_manager:
    def __init__(self):
        self.status = None
        self.errCode = None
        self.errMsg = None
        self.data = None
        self.user_type = ''
        # 依據要回傳給前端的字典格式建立空的self字典
        # response_msg字典裏面又包含兩層字典
        # 因為感覺之後會直接叫裡面的字典來修改、再更新較外層的字典,
        # 因此先將這幾層字典都設 self 
        self.response_msg_key = ['chatroomID','chatUnreadMessageQty', 'chatUserID', 'chatUserType',
                        'chatUserName', 'chatUsergender','chatUserPath', 'messageInfo']
        
        self.response_msg = dict()
        for key in self.response_msg_key:
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
        # 預約功能還沒做但先制定好會回傳的格式
        booking_pattern = 'bookingID:1 ; bookingLeesonID:1; bookingStatus:wait;\
                                      bookingDate:2020-10-10; bookingTime: 12:00-1:00; bookingUpdateTime:'+ str(datetime.now())
        system_msg_pattern = 'bookingDate:2020-10-10; bookingTime: 12:00-1:00'
        
        #self.booking_related_message_dict = dict()
        #for key in booking_related_message_key:
        #    self.booking_related_message_dict[key] = None
        #self.message_info['bookingRelatedMessage'] = self.booking_related_message_dict
        # 註解掉因為現在回傳用不到這個字典
        # 因為booking資訊是在message裡面，先更新message字典再把message字典更新到info大字典
        #self.response_msg['messageInfo'] = self.message_info_group

    # 建立一些error回應
    def response_to_frontend(self, check_result):
        if check_result == 1:
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Query failed'
    # 為了讓user之後能即時收到第一次建立聊天室時的資訊,
    # 要先建立與系統的聊天室作為通道
    # account建立時會叫這個def
    def create_system2user_chatroom(self,**kwargs):
    # user註冊時call來建立聊天室
        user_authID = kwargs['userID']
        user_type = kwargs['user_type']
        systemID = 1 # 1 暫定為系統專用auth_id
        if user_type == 'student':
            chatroom_type = 'system2student'
        elif user_type == 'teacher':
            chatroom_type = 'system2teacher'
        else:
            pass
        new_chatroom = chatroom_info_Mr_Q2user.objects.create(user_auth_id=user_authID,
                user_type = user_type, system_user_auth_id = systemID,
                chatroom_type = chatroom_type)
        new_chatroom.save()        
        print('建立系統聊天室')

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
                # 當聊天室建立時, 系統自動產生一筆訊息, 以便前端推播到最前面
                first_system_msg = chat_history_user2user.objects.create(    
                    chatroom_info_user2user_id = new_chatroom.id,    
                    teacher_auth_id = teacher_authID,    
                    student_auth_id = student_authID, parent_auth_id = -1,       # 現在parent_auth_id預設都是-1
                    message = '於'+ datetime.now().strftime('%H:%M') +'創立聊天室',
                    message_type = 1 ,# 0:一般文字, 1:系統訊息, 2:預約方塊
                    who_is_sender = 'system' ,   # teacher/student/parent/system
                    sender_auth_id = 1,
                    is_read = 0)

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
        self.data = list()
        try:
            # 首先篩選出所有這個人的聊天室
            user_type = kwargs['user_type']
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
                    chatUsergender = chat_user.is_male
                     # chatUnreadMessageQty 歷史訊息的id = roomid,且發送者不是 user, 且未讀 = 0
                    chat_history_obj = chat_history_user2user.objects.filter(Q(chatroom_info_user2user_id=chatroomID)&Q(is_read = 0)& ~Q(who_is_sender = kwargs['userID']))
                    chatUnreadMessageQty = len(chat_history_obj)
                    update_response_msg = {'chatroomID':chatroomID,'chatUnreadMessageQty':chatUnreadMessageQty,
                    'chatUserID' : chatUserID, 'chatUserType': chatUserType ,'chatUsergender':chatUsergender,
                                'chatUserName' : chatUserName, 'chatUserPath' : chatUserPath}
                    a_chatroom_info.update(update_response_msg)
                # messageInfo 每一則訊息的資訊
                # messageType: 訊息類別(0:一般文字, 1:系統訊息, 2:預約方塊)
                    all_messages = chat_history_user2user.objects.filter(chatroom_info_user2user_id=chatroomID).order_by("created_time")
                    if len(all_messages) > 0:
                        message_info_group = list()
                        for a_message in all_messages:
                            temp_info = dict()
                            temp_info['senderID'] = a_message.sender_auth_id
                            temp_info['messageType'] = a_message.message_type
                            temp_info['messageText'] = a_message.message
                            temp_info['messageCreateTime'] = a_message.created_time
                            # 這個system code目前暫時沒有作用, 只是讓前端知道是系統訊息而已
                            # 前端預想之後可能依照這個號碼來做不同動作
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


class websocket_manager:
    def __init__(self):
        # 系統的authID
        self.system_authID = 1 
    def check_authID_type(self, authID):
        # 判斷某個ID的身分
        if authID == self.system_authID: # 目前1是system的auth_id
            self.user_type = 'system'
        else:
            _find_teacher = teacher_profile.objects.filter(auth_id=authID).count()
            _find_student = student_profile.objects.filter(auth_id=authID).count()

            if _find_teacher > 0:
                self.user_type = 'teacher'
            elif _find_student > 0 :
                self.user_type = 'student'
            else: # 等到預約寫了這邊還會再加上預約(system)
                # 1224由於當初架構只分老師和學生,目前系統身分是'老師',
                # 所以系統的身分先給老師, unknown先保留做為沒資料時避免程式壞掉用
                self.user_type = 'unknown'
    
    # 儲存聊天訊息到 db
    # user_2_user
    def chat_storge(self, **kwargs):
        self.chatroom_id = kwargs['chatroomID']
        self.sender = kwargs['senderID'] # 發訊息者
        message = kwargs['messageText']
        messageType = kwargs['messageType']
        chatroom_type = kwargs['chatroom_type']
        self.check_authID_type(self.sender) # 發訊息者的身分
        
        try:
            if chatroom_type == 'user2user':
                chatroom_info = chatroom_info_user2user.objects.filter(id = self.chatroom_id).first()
                print(chatroom_info)
                print(chatroom_info.id)
                if self.user_type == 'student':
                    # 發送者是學生
                    self.teacher_id = chatroom_info.teacher_auth_id
                    self.student_id = self.sender
                elif self.user_type == 'teacher':
                    self.teacher_id = self.sender
                    self.student_id= chatroom_info.student_auth_id
                else:
                    pass
                parent_auth_id = -1 # 目前先給-1
                
                new_msg = chat_history_user2user.objects.create(
                        chatroom_info_user2user_id= self.chatroom_id,
                        teacher_auth_id =self.teacher_id,
                        student_auth_id= self.student_id,
                        parent_auth_id =parent_auth_id,
                        message = message,
                        message_type= messageType,
                        who_is_sender= self.user_type,
                        sender_auth_id = self.sender,
                        is_read= 0,
                        )
                new_msg.save()

                return(new_msg.id, new_msg.created_time)
            
            else: # chatroom_type == 'system2user'
                chatroom_info = chatroom_info_mr_q2user.objects.filter(id = self.chatroom_id).first()
                print(chatroom_info)
                print(chatroom_info.id)
                
                new_msg = chat_history_mr_q2user.objects.create(
                        chatroom_info_system2user_id= self.chatroom_id,
                        user_auth_id = chatroom_info.user_auth_id,
                        system_user_auth_id = chatroom_info.system_user_auth_id,
                        message = message,
                        message_type= messageType,
                        who_is_sender= self.user_type,
                        sender_auth_id = self.sender,
                        is_read= 0,
                        )
                new_msg.save()

                return(new_msg.id, new_msg.created_time)


        except Exception as e:
            print(e)
    
    # 特殊情況1
    # 找尋user和user是不是第一次聊天(目前只有學生對老師需做此特殊處理)
    # 如果是, 查詢他找的新老師與系統的聊天室id資訊並回傳
    def query_chat_history(self, senderID):
        if self.user_type == 'student':
            total = chat_history_user2user.objects.filter(Q(student_auth_id=self.student_id)&Q(teacher_auth_id=self.teacher_id))
            if len(total) <2 : # 當user跟系統聊天的時候才會發生<2,因為system_authID不會在user2user出現
                return('0')
            # 第一筆是系統在聊天室建立時自動發送的訊息
            # 第二筆是學生剛發送的訊息, 所以=2 筆的話表示是新老師
            if len(total)==2:
                print('self.teacher_id:')
                print(self.teacher_id)
                #find_layer = layer_info_maneger.show_channel_layer_info(self.teacher_id)
                chatroomID = chatroom_info_Mr_Q2user.objects.filter(user_auth_id =  self.teacher_id).first()
                self.system_chatroomID = 'system'+ str(chatroomID.id)
                return(self.system_chatroomID)
            else:
                return('0')
        else: 
            return('0')    

    # 特殊情況1的系統回傳
    def msg_maker1_system_2teacher(self, chatroomID):

        send_to_ws = {
            'type' : "chat.message",
            'chatroomID':self.system_chatroomID, # 老師與系統聊天室
            'senderID': self.system_authID, # 系統的auth_id
            'messageText':'',
            'messageType': 2, # 系統方塊
            'systemCode':1, # 建立聊天室
            'messageCreateTime': str(datetime.now())
            }

        messageText = {
            'Aim':'聊天室資訊', #系統方塊標的
            'Title':'新學生通知', #系統方塊標題文字
            'Subtitle':'', #系統方塊副標文字
            'Content': '有新學生已透過聊天室向您聯繫', #系統方塊內容文字
            'BtnText': '立即前往', #系統方塊按鈕文字
            'BtnCode': chatroomID #系統方塊按鈕代碼(學生與老師新聊天室序號)
        }
        send_to_ws['messageText']= messageText 

        return(send_to_ws)

    def msg_system_student_payment_remind(self, **kwargs): 
        # 購買課程的小提醒
        price = kwargs['price']
        #測試用的user                
        #student_authID = 1
        student_authID = kwargs['studenID']
        teacher_authID = kwargs['teacherID']
        lesson_id = kwargs['lessonID']
        lesson_set = kwargs['lesson_set']

        msg_text = f'哈囉！感謝你購買了【{order_teacher}】老師的【{order_lesson}】\
            ，總金額為【{price}】。請於5日內匯款並於「我的存摺頁」填寫匯款帳號'
        return(send_to_ws)  

    


            
    