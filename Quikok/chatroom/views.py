from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from .models import (Messages, chat_room, chatroom_info_Mr_Q2user,chat_history_Mr_Q2user)
from .chat_tools import chat_room_manager
from account.models import student_profile, teacher_profile
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
# FOR API
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
from django.middleware.csrf import get_token
from datetime import datetime, timedelta
import shutil, logging, json
from chatroom.email_sending import chatroom_email_for_edony
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig(level=logging.NOTSET) #DEBUG
logger_chatroom = logging.getLogger('chatroom_info')
#email_info_test =logging.getLogger('mail_admins')

# 寄信到edony的email
chatroom_email_edony_notification = chatroom_email_for_edony()

# 例項化
scheduler = BackgroundScheduler()
# 每間隔24小時執行一次, 只設定起始時間
# st = time()

def check_if_edony_chatroom_unread():
    unread_msg = chat_history_Mr_Q2user.objects.filter(system_is_read = 0,user_is_read =1).count()
    if unread_msg != 0:
        chatroom_email_edony_notification.edony_unread_user_msg(unread_msg)
        logger_chatroom.info('chatroom.view 例行檢查，寄出未讀訊息')
scheduler.add_job(check_if_edony_chatroom_unread, 'interval',
    hours = 8, start_date = '2021-04-12 01:01:00')
logger_chatroom.info('chatroom.view 例行檢查是否有未讀訊息')
    # hours = 24
   #,end_date = '2021-02-02 10:31:00' seconds, minutes, hours
scheduler.start()

# 確認聊天室是否存在、不存在的話建立聊天室
@require_http_methods(['POST'])
def check_if_chatroom_exist(request):
    response = dict()
    pass_data_to_chat_tools = dict()
    key_from_request = ['userID', 'chatUserID']
    token_from_user_raw = request.headers.get('Authorization', False)
    
    for key_name in key_from_request:
        value = request.POST.get(key_name ,False)
        pass_data_to_chat_tools[key_name] = value
    
    pass_data_to_chat_tools['token'] = token_from_user_raw
    logging.info(f"chatroom/views:回傳或建立系統聊天室:{pass_data_to_chat_tools}")
    
    if False in pass_data_to_chat_tools.values():    
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed.'
        response['data'] = None
        return JsonResponse(response)
    else:
        token = token_from_user_raw.split(' ')[1]
        pass_data_to_chat_tools['token'] = token

        chat_manager = chat_room_manager()
        response['status'], response['errCode'], response['errMsg'], response['data'] =\
        chat_manager.check_and_create_chat_room(**pass_data_to_chat_tools)
        return JsonResponse(response)

# 確認系統聊天室是否存在、回傳聊天室ID
@require_http_methods(['POST'])
def check_system_chatroom(request):
    response = dict()
    pass_data_to_chat_tools = dict()

    userID = request.POST.get('userID' ,False)
    token_from_user_raw = request.headers.get('Authorization', False)
    token = token_from_user_raw.split(' ')[1]
    pass_data_to_chat_tools['token'] = token
    
    if False in [userID, token]:    
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed.如問題持續麻煩聯絡我們!'
        response['data'] = None
        return JsonResponse(response)

    else:
        try:
            # 檢查是否存在,理論上user註冊時就會建立一個唯一的房間,所以沒找到或超過1的話就failed
            system_chatroom_query = chatroom_info_Mr_Q2user.objects.filter(user_auth_id = userID)
            if len(system_chatroom_query) != 1 :
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = 'Query Failed.聊天室不存在。如問題持續麻煩聯絡我們!'
                response['data'] = None
                return JsonResponse(response)
            
            else:
                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
                response['data'] = {'chatroomID':'system'+str(system_chatroom_query.first().id)}
                return JsonResponse(response)
        except Exception as e:
            logging.error(f"chatroom/views:check_system_chatroom except error:{e}", exc_info=True)
            response['status'] = 'failed'
            response['errCode'] = '2'
            response['errMsg'] = '資料庫有問題，如狀況持續麻煩您聯絡客服！'
            response['data'] = None
            return JsonResponse(response)

# 回傳一般聊天室歷史紀錄
def chatroom_content(request):
    response = dict()
    pass_data_to_chat_tools = dict()
    key_from_request = ['userID', 'user_type'] 
    token_from_user_raw = request.headers.get('Authorization', False)
    token = token_from_user_raw.split(' ')[1]
    pass_data_to_chat_tools['token'] = token
    logging.info(f"chatroom/views:chatroom_content.聊天室收到的token:{token}")

    for key_name in key_from_request:
        value = request.POST.get(key_name ,False)
        pass_data_to_chat_tools[key_name] = value
    
    print(pass_data_to_chat_tools)
    if False in pass_data_to_chat_tools.values():    
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed.'
        response['data'] = None
        logging.error("chatroom/views:chatroom_content Received Arguments Failed.", exc_info=True)
        return JsonResponse(response)

    else:        
        chat_manager = chat_room_manager()
        response['status'], response['errCode'], response['errMsg'], response['data'] =\
        chat_manager.chat_main_content(**pass_data_to_chat_tools)
        
        return JsonResponse(response)

# 回傳系統聊天室歷史紀錄
def system_chatroom_content(request):
    response = dict()
    pass_data_to_chat_tools = dict()
    userID = request.POST.get('userID',False) 
    token_from_user_raw = request.headers.get('Authorization', False)
    token = token_from_user_raw.split(' ')[1]
    pass_data_to_chat_tools['token'] = token
    logging.info(f"chatroom/views:chatroom_content.聊天室收到的token:{token}")
    

    if False in [userID, token]:    
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed.'
        response['data'] = None
        logging.error("chatroom/views:chatroom_content Received Arguments Failed.", exc_info=True)
        return JsonResponse(response)

    else:        
        chat_manager = chat_room_manager()
        response['status'], response['errCode'], response['errMsg'], response['data'] =\
        chat_manager.system_chat_main_content(userID)
        
        return JsonResponse(response)


# 這個api:54會將指定聊天室裡該user是否已讀的狀態全部改為 is_read
def update_user2user_chatroom_msg_is_read(request):
    response = dict()
    userID = request.POST.get('userID' ,False)
    user_type = request.POST.get('type' ,False)
    chatroomID = request.POST.get('userID' ,False)
    token_from_user_raw = request.headers.get('Authorization', False)
    token = token_from_user_raw.split(' ')[1]

    if False in [userID, user_type, chatroomID, token]:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '資料傳輸有問題，如狀況持續麻煩您聯絡客服！'
        response['data'] = None
        return JsonResponse(response)
    else:
        try:
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = None
            return JsonResponse(response)
        except Exception as e:
            print(e)
            logging.error("chatroom/views:update_user2user_chatroom_msg_is_read.Exception:{e}", exc_info=True)
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '資料庫有問題，如狀況持續麻煩您聯絡客服！'
            response['data'] = None
            return JsonResponse(response)
        # 查詢user身分, 以此來決定是 student_is_read 還是 teacher_is_read要update

