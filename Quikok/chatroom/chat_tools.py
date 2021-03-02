from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from .models import *
from account.models import student_profile, teacher_profile
from datetime import datetime
from account.auth_tools import auth_check_manager
from .system_2user_layer import layer_info_maneger
import logging

logging.basicConfig(level=logging.NOTSET) #DEBUG

class chat_room_manager:
    def __init__(self):
        self.parent_auth_id = -1 # 目前尚未定義,因此全部都給-1
        self.status = None
        self.errCode = None
        self.errMsg = None
        self.data = None
        self.user_type = ''
        self.chatroom_type = ''
        self.system_authID = 1
        # 依據要回傳給前端的字典格式建立空的self字典
        # response_msg字典裏面又包含兩層字典
        # 因為感覺之後會直接叫裡面的字典來修改、再更新較外層的字典,
        # 因此先將這幾層字典都設 self 
        self.response_msg_key = ['chatroomID','chatroom_type','chatUnreadMessageQty', 'chatUserID', 'chatUserType',
                        'chatUserName', 'chatUsergender','chatUserPath', 'messageInfo']
        
        self.response_msg = dict()
        for key in self.response_msg_key:
            self.response_msg[key] = None
        #a_message_info_dict_keys = ['userID','messageID','messageType','messageText','bookingRelatedMessage', 
        #                            'systemCode', 'messageCreateTime']
        # = list()
        #self.a_message_info = dict()
        #for key in a_message_info_dict_keys:
        #    self.a_message_info[key] = None  
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
    # user註冊時call來建立系統聊天室
        user_authID = kwargs['userID']
        user_type = kwargs['user_type']
        #systemID = self.system_authID # 1 暫定為系統專用auth_id

        if user_type == 'student':
            chatroom_type = 'system2student'
        elif user_type == 'teacher':
            chatroom_type = 'system2teacher'
        else:
            pass
        new_chatroom = chatroom_info_Mr_Q2user.objects.create(
            user_auth_id = user_authID,
            user_type = user_type, 
            system_user_auth_id = self.system_authID,
            chatroom_type = chatroom_type)
        new_chatroom.save()
        logging.info(f"chatroom/chat_tools:建立系統聊天室")

        # 當聊天室建立時, 系統自動產生2筆訊息, 以便使前端排序不會出錯 + 讓user知道有客服
        first_system_msg = chat_history_Mr_Q2user.objects.create(    
            chatroom_info_system2user_id = new_chatroom.id,    
            system_user_auth_id = self.system_authID,    
            user_auth_id = user_authID, 
            message = '於'+ datetime.now().strftime('%H:%M') +'創立聊天室',
            message_type = 'auto_system_msg' , #系統訊息
            who_is_sender = 'system' ,   # teacher/student/parent/system
            sender_auth_id = self.system_authID,
            system_is_read = True,
            user_is_read = False)
        logging.info('create system2user 1st msg.')

        welcom_system_msg = chat_history_Mr_Q2user.objects.create(    
            chatroom_info_system2user_id = new_chatroom.id,    
            system_user_auth_id = self.system_authID,    
            user_auth_id = user_authID, 
            message = '嗨！我是Quikok！開課的客服專家QQ球雀，有建議或是網站問題回報都可以找我唷！啾啾～',
            message_type = 'text_msg' , #系統訊息
            who_is_sender = 'system' ,   # teacher/student/parent/system
            sender_auth_id = self.system_authID,
            system_is_read = True,
            user_is_read = False)
        logging.info('create system2user 2nd msg.')
        

    def check_and_create_chat_room(self,**kwargs):
        # 確認聊天室是否存在,存在的話回傳ID,不存在的話建立再回傳ID
        user_authID = kwargs['userID'] 
        chatuser_authID = kwargs['chatUserID']
        parent_authID = self.parent_auth_id #暫時未使用因此設 -1
        chatroom_type = 'teacher2student' # 暫時只有這種

        try:
            # 首先確認發msg的user身分
            check_tool = auth_check_manager()
            user_type = check_tool.check_user_type(user_authID)
            chatuser_type = check_tool.check_user_type(user_authID)
            
            if user_type==0 or chatuser_type == 0:
                # 找不到人
                self.status = 'failed'
                self.errCode = '1'
                self.errMsg = 'Querying Data Failed.'
                return (self.status, self.errCode, self.errMsg, self.data)
            
            #elif user_type == 'system' or chatuser_type == 'system':
                # 因為system2user的聊天室是使用者在註冊的時候就建立了,
                # 因此這邊只需要回傳id, 不用再建立(理論上")
            #    system_chatroom_query = chatroom_info_Mr_Q2user.objects.filter/
            #        (Q(user_auth_id = chatuser_authID)&Q(system_user_auth_id = user_authID))

            elif user_type == 'teacher':
            # 正常來說聊天室只會有唯一一個存在, 超過就有問題
                chatroom = chatroom_info_user2user.objects.filter(
                    Q(student_auth_id=chatuser_authID)&Q(teacher_auth_id=user_authID))
                student_authID = chatuser_authID
                teacher_authID = user_authID
            elif user_type =='student':
                chatroom = chatroom_info_user2user.objects.filter(
                    Q(student_auth_id=chatuser_authID)&Q(teacher_auth_id=user_authID))
                student_authID = user_authID
                teacher_authID = chatuser_authID
            
            if len(chatroom) == 0 :
                # 聊天室尚未存在,要新建立
                new_chatroom = chatroom_info_user2user.objects.create(student_auth_id=student_authID,
                    teacher_auth_id=teacher_authID, parent_auth_id = parent_authID,
                    chatroom_type = chatroom_type)
                # 當聊天室建立時, 系統自動產生一筆訊息, 以便前端推播到最前面
                first_system_msg = chat_history_user2user.objects.create(    
                    chatroom_info_user2user_id = new_chatroom.id,    
                    teacher_auth_id = teacher_authID,    
                    student_auth_id = student_authID, parent_auth_id = parent_authID, # 現在parent_auth_id預設都是-1
                    message = '於'+ datetime.now().strftime('%H:%M') +'創立聊天室',
                    message_type = 'auto_system_msg' , #系統訊息
                    who_is_sender = 'system' ,   # teacher/student/parent/system
                    sender_auth_id = self.system_authID,
                    teacher_is_read = True,
                    student_is_read = False)
                logging.info('create new user2user chatroom')
                
                self.status = 'success'
                self.errCode = None
                self.errMsg = None
                self.data = {'chatroomID' : new_chatroom.id}
                return (self.status, self.errCode, self.errMsg, self.data)
                               
            elif len(chatroom) == 1 :
                print('their chatroom already exist')
                self.status = 'success'
                self.errCode = None
                self.errMsg = None
                self.data = {'chatroomID' : chatroom[0].id}
                return (self.status, self.errCode, self.errMsg, self.data)
            else:
                print('something wrong...find multi chatrooms')
                self.status = 'failed'
                self.errCode = '1'
                self.errMsg = 'Querying Data Failed.'
                return (self.status, self.errCode, self.errMsg, self.data)
        except Exception as e:
            print(e)
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Querying Data Failed.'
            return (self.status, self.errCode, self.errMsg, self.data)

    # 調出主對話框全部內容
    # kwargs: userID, user_type
    def chat_main_content(self, **kwargs):
        self.data = list()
        try:
            # 首先篩選出所有這個人的聊天室
            user_type = kwargs['user_type']
            room_queryset= chatroom_info_user2user.objects.filter(
                Q(student_auth_id=kwargs['userID'])|Q(teacher_auth_id=kwargs['userID'])).order_by("created_time")
            logging.info(f'chat_tools room_queryset info:使用者有這些聊天室{room_queryset}')
            
            # 如果有資料的前提(not none)包成可以回傳給前端的格式
            if room_queryset is not None:
                response_data = list()
                for a_chatroom in room_queryset:
                    a_chatroom_info = dict()
                    for key in self.response_msg_key:
                        a_chatroom_info[key] = None # 建立要回傳給前端的字典結構, values尚未填入
                    chatroomID = a_chatroom.id
                    if user_type == 'teacher':
                        chatUserID = a_chatroom.student_auth_id
                        chat_user = student_profile.objects.filter(auth_id = chatUserID).first()
                        chatUserType = 'student'                  
                        #chatUnreadMessageQty 未讀訊息計算分為老師跟學生      
                        chat_history_set = chat_history_user2user.objects.filter\
                            (Q(chatroom_info_user2user_id=chatroomID)&Q(teacher_is_read = False))
                    elif user_type == 'student':
                        chatUserID = a_chatroom.teacher_auth_id
                        chat_user = teacher_profile.objects.filter(auth_id = chatUserID).first()
                        chatUserType = 'teacher'
                        chat_history_set = chat_history_user2user.objects.filter\
                            (Q(chatroom_info_user2user_id=chatroomID)&Q(student_is_read = False))
                    else: # 將來可能有其他類別
                        pass
                    chatUnreadMessageQty = chat_history_set.count()
                    
                    # 對方可能會沒有大頭貼
                    if len(chat_user.thumbnail_dir) > 0:
                        #print(chat_user.thumbnail_dir)
                        chatUserPath = chat_user.thumbnail_dir
                    else:
                        chatUserPath = ''
                    chatUserName = chat_user.nickname
                    chatUsergender = chat_user.is_male

                    # chatUnreadMessageQty 歷史訊息的id = roomid,且發送者不是 user, 且未讀 = 0
                    #chat_history_set = chat_history_user2user.objects.filter(Q(chatroom_info_user2user_id=chatroomID)&Q(is_read = 0)& ~Q(who_is_sender = kwargs['userID']))
                    
                    update_response_msg = {'chatroomID':chatroomID,'chatroom_type': 'user2user','chatUnreadMessageQty':chatUnreadMessageQty,
                    'chatUserID' : chatUserID, 'chatUserType': chatUserType ,'chatUsergender':chatUsergender,
                                'chatUserName' : chatUserName, 'chatUserPath' : chatUserPath}
                    a_chatroom_info.update(update_response_msg)

                # messageInfo 每一則訊息的資訊
                # messageType: 訊息類別(0:一般文字, 1:系統訊息, 2:預約方塊)
                    all_messages = chat_history_user2user.objects.filter(chatroom_info_user2user_id=chatroomID).order_by("created_time")
                    # Query 該聊天室的全部訊息
                    if all_messages is not None:
                        message_info_group = list()
                        for a_message in all_messages:
                            temp_info = dict()
                            temp_info['senderID'] = a_message.sender_auth_id
                            temp_info['messageType'] = a_message.message_type
                            temp_info['messageText'] = a_message.message
                            temp_info['messageID'] = a_message.id
                            temp_info['messageCreateTime'] = a_message.created_time
                            # 這個system code目前暫時只是讓前端區分是系統訊息還是一般而已
                            # 前端預想之後可能依照這個號碼來做不同動作,可能會需要改成新增model來記錄
                            if user_type == 'teacher':
                                if a_message.teacher_is_read == True:
                                    temp_info['messageStatus'] = 'read'
                                else:
                                    temp_info['messageStatus'] = 'unread'
                            else:
                                if a_message.student_is_read == True:
                                    temp_info['messageStatus'] = 'read'
                                else:
                                    temp_info['messageStatus'] = 'unread'

                            if a_message.message_type == 'auto_system_msg':
                                temp_info['systemCode'] = 'no_action' 
                            else:
                                temp_info['systemCode'] = 'user2user'
                            message_info_group.append(temp_info)
                        
                            logging.info(f'chat_tools chat_history info:每一則歷史訊息的資訊:{temp_info}')
                    else:
                        message_info_group = list()

                    a_chatroom_info['messageInfo'] = message_info_group 
                    response_data.append(a_chatroom_info)
                #print(response_data)
                self.status = 'success'
                self.data = response_data
            else: # 尚未建立任何聊天室
                self.status = 'success'
            return (self.status, self.errCode, self.errMsg, self.data)
        
        except:
            logging.error("chatroom/chat_tools:chatroom_content exception.", exc_info=True)
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Querying Data Failed.'
            return (self.status, self.errCode, self.errMsg, self.data)

    
    # 調出系統聊天室中對話框全部內容
    # userID 可能是系統或user    
    def system_chat_main_content(self, user_authID):
        self.data = list()
        try:
            # 首先確認查詢歷史msg的user身分
            check_tool = auth_check_manager()
            user_type = check_tool.check_user_type(user_authID)
            logging.info(f'chat_tools system user_authID is:{user_authID}')
            logging.info(f'chat_tools system user_type is:{user_type}')
            if user_type == 0:
                # 找不到user類別
                self.status = 'failed'
                self.errCode = '2'
                self.errMsg = 'Querying Data Failed.'
                return (self.status, self.errCode, self.errMsg, self.data)
            else:
                # 篩選出所有這個人的聊天室,目前理論上user只會有唯一一個與系統的聊天室,但系統對user會有很多個
                room_queryset= chatroom_info_Mr_Q2user.objects.filter(
                    Q(user_auth_id= user_authID)|Q(system_user_auth_id=user_authID)).order_by("created_time")
                
                logging.info(f'chat_tools room_queryset info:使用者有這些系統聊天室{room_queryset}')
                
            # 如果有資料的前提(not none)包成可以回傳給前端的格式
            if room_queryset is not None:
                response_data = list()
                for a_chatroom in room_queryset:
                    a_chatroom_info = dict()
                    for key in self.response_msg_key:
                        a_chatroom_info[key] = None # 建立要回傳給前端的字典結構, values尚未填入
                    chatroomID = a_chatroom.id
                    if user_type == 'system': # 目前的system auth_id=1是老師
                        chatUserID = a_chatroom.user_auth_id
                        chat_user_type = check_tool.check_user_type(chatUserID)
                        # 聊天對象可能是學生or老師
                        if chat_user_type == "teacher":
                            chat_user = teacher_profile.objects.filter(auth_id = chatUserID).first()
                            chatUserType = "teacher"
                        elif chat_user_type == "student":
                            chat_user = student_profile.objects.filter(auth_id = chatUserID).first()
                            chatUserType = "student"
                        # 下面的chatUnreadMessageQty 未讀訊息計算分為user未讀或system未讀,所以一起在這邊做      
                        chat_history_set = chat_history_Mr_Q2user.objects.filter\
                            (Q(chatroom_info_system2user_id = chatroomID)&Q(system_is_read = False))
                        logging.info(f'chat_tools system chatuser type is:{chatUserType}')
                    else: # user type = 老師或學生, 那聊天對象就是 system, system目前是老師
                        chatUserID = a_chatroom.system_user_auth_id
                        chat_user = teacher_profile.objects.filter(auth_id = chatUserID).first()
                        chatUserType = 'system'
                        # 下面的chatUnreadMessageQty 未讀訊息計算分為user或system,所以一起在這邊做
                        chat_history_set = chat_history_Mr_Q2user.objects.filter\
                            (Q(chatroom_info_system2user_id=chatroomID)&Q(user_is_read = False))
                    
                        logging.info(f'chat_tools system chatuser type is:{chatUserType}')
                
                    chatUnreadMessageQty = chat_history_set.count()
                    
                    # 對方可能會沒有大頭貼
                    if len(chat_user.thumbnail_dir) > 0:
                        #print(chat_user.thumbnail_dir)
                        chatUserPath = chat_user.thumbnail_dir
                    else:
                        chatUserPath = ''
                    chatUserName = chat_user.nickname
                    chatUsergender = chat_user.is_male

                    # chatUnreadMessageQty 歷史訊息的id = roomid,且發送者不是 user, 且未讀 = 0
                    #chat_history_set = chat_history_user2user.objects.filter(Q(chatroom_info_user2user_id=chatroomID)&Q(is_read = 0)& ~Q(who_is_sender = kwargs['userID']))
                    
                    update_response_msg = {'chatroomID':chatroomID, 'chatroom_type': 'system2user','chatUnreadMessageQty':chatUnreadMessageQty,
                    'chatUserID' : chatUserID, 'chatUserType': chatUserType ,'chatUsergender':chatUsergender,
                                'chatUserName' : chatUserName, 'chatUserPath' : chatUserPath}
                    a_chatroom_info.update(update_response_msg)
                # messageInfo 每一則訊息的資訊
                # messageType: 訊息類別(0:一般文字, 1:系統訊息, 2:預約方塊)
                    all_messages = chat_history_Mr_Q2user.objects.filter\
                        (chatroom_info_system2user_id=chatroomID).order_by("created_time")
                    # Query 該聊天室的全部訊息
                    if all_messages is not None:
                        message_info_group = list()
                        for a_message in all_messages:
                            temp_info = dict()
                            temp_info['senderID'] = a_message.sender_auth_id
                            temp_info['messageType'] = a_message.message_type
                            temp_info['messageText'] = a_message.message
                            temp_info['messageID'] = a_message.id
                            temp_info['messageCreateTime'] = a_message.created_time
                            # 這個system code目前暫時只是讓前端區分是系統訊息還是一般而已
                            # 前端預想之後可能依照這個號碼來做不同動作,可能會需要改成新增model來記錄
                            if user_type == 'system':
                                if a_message.system_is_read == True:
                                    temp_info['messageStatus'] = 'read'
                                else:
                                    temp_info['messageStatus'] = 'unread'
                            else:
                                if a_message.user_is_read == True:
                                    temp_info['messageStatus'] = 'read'
                                else:
                                    temp_info['messageStatus'] = 'unread'

                            if a_message.message_type == 'auto_system_msg':
                                temp_info['systemCode'] = 'no_action' 
                            else:
                                temp_info['systemCode'] = 'user2user'
                            message_info_group.append(temp_info)
                    else:
                        message_info_group = list()

                    a_chatroom_info['messageInfo'] = message_info_group 
                    response_data.append(a_chatroom_info)
                
                self.status = 'success'
                self.data = response_data

            else: # 沒有任何聊天室,理論上不存在這個情況
                logging.error("chatroom/chat_tools:system_chat_main_content error.找不到系統聊天室", exc_info=True)
                self.status = 'failed'
                self.errCode = '3'
                self.errMsg = 'Querying Data Failed.如狀況持續麻煩透過e-mail或電話聯絡客服'
            
            return (self.status, self.errCode, self.errMsg, self.data)
        
        except:
            logging.error("chatroom/chat_tools:chatroom_content exception.", exc_info=True)
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Querying Data Failed.如狀況持續麻煩透過e-mail或電話聯絡客服'
            return (self.status, self.errCode, self.errMsg, self.data)

class websocket_manager:
    def __init__(self):
        # 系統的authID
        self.system_authID = 1 
        self.parent_auth_id = -1 # 還沒用到先都給-1
        self.user_type = ''
        #self.teacher_id = ''
        #self.student_id = ''
        self.chatroom_id = ''
        self.sender = ''

    def check_authID_type(self, authID):
        # 判斷某個ID的身分
        if type(authID) == str:
            authID = int(authID)
        if authID == self.system_authID: # 目前1是system的auth_id
            self.user_type = 'system'
        else:
            _find_teacher = teacher_profile.objects.filter(auth_id=authID)
            _find_student = student_profile.objects.filter(auth_id=authID)

            if _find_teacher.count() > 0 :
                self.user_type = 'teacher'
            elif _find_student.count() > 0 :
                self.user_type = 'student'
            else: # 等到預約寫了這邊還會再加上預約(system)
                # 1224由於當初架構只分老師和學生,目前系統身分是'老師',
                # 所以系統的身分先給老師, unknown先保留做為沒資料時避免程式壞掉用
                self.user_type = 'unknown'
        
        logging.info(f"chatroom/chat_tools:check_authID_type, authID is:{authID}")
        logging.info(f"chatroom/chat_tools:check_authID_type, authID type is:{type(authID)}")
        logging.info(f"chatroom/chat_tools:check_authID_type, user type is:{self.user_type}")
        
        


    # 儲存聊天訊息到 db
    # user_2_user & system2user
    def chat_storge(self, **kwargs):
        self.chatroom_id = kwargs['chatroomID']
        self.sender = kwargs['senderID'] # 發訊息者
        message = kwargs['messageText']
        messageType = kwargs['messageType']
        self.chatroom_type = kwargs['chatroom_type']
        self.check_authID_type(self.sender) # 發訊息者的身分
        logging.info(f"chatroom/consumer:\n\n storge check user_type:{self.user_type}", exc_info=True)
                
        try:
            if self.chatroom_type == 'user2user':
                chatroom_info = chatroom_info_user2user.objects.filter(id = self.chatroom_id).first()
                logging.info(f"chatroom/consumer:\n\n storge start user2user message.chatroomID:{chatroom_info}", exc_info=True)
                
                if self.user_type == 'student':
                    # 發送者是學生
                    teacher_id = chatroom_info.teacher_auth_id     
                    new_msg = chat_history_user2user.objects.create(
                        chatroom_info_user2user_id= self.chatroom_id,
                        teacher_auth_id = teacher_id,
                        student_auth_id= self.sender,
                        parent_auth_id = self.parent_auth_id,
                        message = message,
                        message_type= messageType,
                        who_is_sender= self.user_type,
                        sender_auth_id = self.sender,
                        teacher_is_read= False,
                        student_is_read = True
                        )
                    new_msg.save()
                elif self.user_type == 'teacher':
                    #發送者是老師
                    self.teacher_id = self.sender
                    self.student_id= chatroom_info.student_auth_id
                    new_msg = chat_history_user2user.objects.create(
                        chatroom_info_user2user_id= self.chatroom_id,
                        teacher_auth_id =self.teacher_id,
                        student_auth_id= self.student_id,
                        parent_auth_id = self.parent_auth_id,
                        message = message,
                        message_type= messageType,
                        who_is_sender= self.user_type,
                        sender_auth_id = self.sender,
                        teacher_is_read= True,
                        student_is_read = False
                        )
                    new_msg.save()

                else:
                    pass

                return(new_msg.id, new_msg.created_time)
            
            else: # chatroom_type == 'system2user'
                chatroom_info = chatroom_info_Mr_Q2user.objects.filter(id = self.chatroom_id).first()
                
                logging.info("chatroom/consumer:\n\nstorge system2user message.{chatroom_info}", exc_info=True)
                
                if self.sender == chatroom_info.system_user_auth_id : # 發言者是系統
                    new_msg = chat_history_Mr_Q2user.objects.create(
                            chatroom_info_system2user_id= self.chatroom_id,
                            user_auth_id = chatroom_info.user_auth_id,
                            system_user_auth_id = chatroom_info.system_user_auth_id,
                            message = message,
                            message_type= messageType,
                            who_is_sender= self.user_type,
                            sender_auth_id = self.sender,
                            system_is_read= True,
                            user_is_read = False
                            )
                    new_msg.save()
                else:
                    new_msg = chat_history_Mr_Q2user.objects.create(
                            chatroom_info_system2user_id= self.chatroom_id,
                            user_auth_id = chatroom_info.user_auth_id,
                            system_user_auth_id = chatroom_info.system_user_auth_id,
                            message = message,
                            message_type= messageType,
                            who_is_sender= self.user_type,
                            sender_auth_id = self.sender,
                            system_is_read= False,
                            user_is_read = True
                            )
                    new_msg.save()

                return(new_msg.id, new_msg.created_time)

        except Exception as e:
            logging.error(f"chatroom/chat_tools:\n\nstorge error message.{e}", exc_info=True)

    
    def update_chat_msg_is_read_status(self, **kwargs):
        #chatroom_id = kwargs['chatroomID']
        userID = kwargs['senderID'] # 要改成已讀的ID
        chatroom_type = kwargs['chatroom_type']
        self.check_authID_type(userID)
        msg_status_update_dict = kwargs['msg_status_update'] # 這邊也會是dict
        update_msgID_list = msg_status_update_dict['messageID'] 
        logging.info(f"chatroom/consumer:\n\n update chat msg is read status IDs:{update_msgID_list}", exc_info=True)
        logging.info(f"chatroom/consumer:\n\n update chat msg is read chatroom_type:{chatroom_type}", exc_info=True)
        logging.info(f"chatroom/consumer:\n\n update chat msg is read userID:{userID}", exc_info=True)
        logging.info(f"chatroom/consumer:\n\n update chat msg is read userID data type:{type(userID)}", exc_info=True)
        logging.info(f"chatroom/consumer:\n\n update chat msg is read user_type:{self.user_type}", exc_info=True)
 
        if chatroom_type == 'user2user':
            if self.user_type == 'student':
                chat_history_user2user.objects.filter(id__in = update_msgID_list).update(student_is_read=True)
                
            else: # 理論上就是老師
                chat_history_user2user.objects.filter(id__in = update_msgID_list).update(teacher_is_read=True)
                
        else:
            if self.user_type == 'system':
                chat_history_Mr_Q2user.objects.filter(id__in = update_msgID_list).update(system_is_read=True)
            
            else: # 老師或學生
                chat_history_Mr_Q2user.objects.filter(id__in = update_msgID_list).update(user_is_read=True)
                

    # 特殊情況: 找尋user和user是不是第一次聊天 02.22 更新老師與學生互相都可能第一次發訊息給對方
    # ...學生跟老師和系統間也可能是第一次互相發msg給對方? 啊不會因為system2user的通道一開始就建立了!
    # 如果是, 查詢他找的新老師與系統的聊天室id資訊並回傳
    def check_if_users_chat_first_time(self, **kwargs):
        
        chatroom_id = kwargs['chatroomID']
        senderID = kwargs['senderID'] # 發訊息者
        self.check_authID_type(senderID) # 發訊息者的身分

        #senderID = kwargs[]
        #chat_userID = 
        logging.info("chatroom/chat_tools:check if users are chating first time")
        logging.info(f"chatroom/chat_tools:check if users are chating first time, user ID is:{senderID}")
        logging.info(f"chatroom/chat_tools:check if users are chating first time, user type is:{self.user_type}")
        if self.user_type == 'student':
            total_chat_history = chat_history_user2user.objects.filter\
                (Q(student_auth_id= senderID)&Q(chatroom_info_user2user_id = chatroom_id))
            logging.info(f"chatroom/chat_tools:check if users are chating first time, chat_history len:{total_chat_history}")
            if len(total_chat_history) != 2 :
                logging.info("chatroom/chat_tools:check done:no (if users are chating first time)", exc_info=True)     
                return(0)
                #return(total_chat_history)
            # 第一筆是系統在聊天室建立時自動發送的訊息
            # 第二筆是學生剛發送的訊息, 所以=2 筆的話表示是新老師
            else: 
                teacher_id = total_chat_history.first().teacher_auth_id
                logging.info(f"chatroom/chat_tools:check teacher_id is :{teacher_id}", exc_info=True)
                # 備註:理論上system_chatroom只會有一個
                system_chatroom = chatroom_info_Mr_Q2user.objects.filter(user_auth_id = teacher_id).first()
                system_chatroomID = system_chatroom.id
                logging.info("chatroom/chat_tools:check done:yes (if users are chating first time)", exc_info=True)     
                logging.info(f"chatroom/chat_tools:and need to send WS to system_chatroomID:{system_chatroomID}", exc_info=True)     
                
                return(system_chatroomID)
            
        else: # 此時 self.user_type == 'teacher'
            total_chat_history = chat_history_user2user.objects.filter\
                (Q(chatroom_info_user2user_id = chatroom_id)&Q(teacher_auth_id = senderID))
            if len(total_chat_history) != 2 : 
                logging.info("chatroom/chat_tools:check done: no (if users are chating first time)", exc_info=True)     
                return(0)
            # 第一筆是系統在聊天室建立時自動發送的訊息
            # 第二筆是老師剛發送的訊息, 所以=2 筆的話表示是新學生
            else: 
                student_id = total_chat_history.first().student_auth_id
                logging.info(f"chatroom/chat_tools:check student_id is : {student_id}", exc_info=True)
                # 備註:理論上system_chatroom只會有一個
                system_chatroom = chatroom_info_Mr_Q2user.objects.filter(user_auth_id = student_id).first()
                system_chatroomID = system_chatroom.id
                logging.info("chatroom/chat_tools:check done: yes (if users are chating first time)", exc_info=True)     
                return(system_chatroomID)

        
    # 特殊情況1, 當user彼此第一次聊天的系統訊息
    def system_auto_msg_when_user_first_chat(self, chatroomID):

        send_to_ws = {
            'type' : "chat.message",
            #'chatroomID':'system'+ str(chatroomID), # user與系統聊天室
            'chatroomID': chatroomID,
            'senderID': self.system_authID, # 系統的auth_id
            'messageText':'',
            'messageType': 'notice_first_msg', # 系統方塊
            'systemCode': 'create_chatroom', # 建立聊天室
            'messageCreateTime': str(datetime.now()),
            'messageID': '',
            'messageTempID': '',
            'messageStatus':'unread'
            }

        messageText = {
            'Aim':'聊天室資訊', #系統方塊標的
            'Title':'新聊天通知', #系統方塊標題文字
            'Subtitle':'', #系統方塊副標文字
            'Content': '有新聯絡對象！', #系統方塊內容文字
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

    


            
    