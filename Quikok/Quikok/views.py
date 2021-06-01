from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import os
import logging
from django.conf import settings
from chatroom.email_sending import chatroom_email_for_edony, chatroom_email_manager
from chatroom.models import chat_history_Mr_Q2user, chat_history_user2user
from account.models import student_profile, teacher_profile
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.NOTSET) #DEBUG

logger_chatroom = logging.getLogger('chatroom_info')
#email_info_test =logging.getLogger('mail_admins')

## 聊天室定時區##
# 寄信到edony的email
chatroom_email_edony_notification = chatroom_email_for_edony()
# 聊天室
chatroom_user_notification =chatroom_email_manager()
# 例項化
scheduler = BackgroundScheduler()

# st = time()
# 每8小時執行一次
def check_if_edony_chatroom_unread():
    unread_msg = chat_history_Mr_Q2user.objects.filter(system_is_read = 0,user_is_read =1).count()
    if unread_msg != 0:
        chatroom_email_edony_notification.edony_unread_user_msg(unread_msg)
        logger_chatroom.info('chatroom.view 例行檢查，寄出未讀訊息')

# 每間隔24小時執行一次, 只設定起始時間
def check_if_teacher_chatroom_unread():
    # 首先列出所有的老師
    all_teacher = teacher_profile.objects.all()
    for teacher in all_teacher:
        # 1,2,3,4,5 系統測試帳號不用特別檢查聊天室
        if teacher.id not in [1]: 
            # 檢查是否有未讀訊息, 若有就寄信通知
            unread_msg = chat_history_user2user.objects.filter(id = teacher.id ,teacher_is_read = 0).exists()
            if unread_msg :
                chatroom_user_notification.email_teacher_chatroom_unread(
                    teacher_authID = teacher.id,
                    teacher_nickname = teacher.nickname ,
                    teacher_email = teacher.username
                )

# 寄給edony的每 8小時檢查
scheduler.add_job(check_if_edony_chatroom_unread, 'interval',
    minutes = 2, start_date = '2021-04-12 01:00:00')
logger_chatroom.info('chatroom.view 例行檢查edony是否有未讀訊息')
    # hours = 24
   #,end_date = '2021-02-02 10:31:00' seconds, minutes, hours

# 寄給客人的每24小時檢查
scheduler.add_job(check_if_teacher_chatroom_unread, 'interval',
    minutes = 2, start_date = '2021-04-12 11:00:00')

scheduler.start()




@require_http_methods(['GET'])
def get_banner_bar(request):
    response = {}
    data = []
    try:
        img_path = os.path.join(settings.BASE_DIR, 'website_assets/homepage')
        # 之後再看這個路徑該怎麼修比較好
        for i, desktop_img in enumerate(os.listdir(os.path.join(img_path, 'desktop'))):
            data.append(
                {
                    'type': 'pc',
                    'sort': str(i),
                    'img_url': f'/static/homepage/desktop/{desktop_img}',
                }
            )
        for i, mobile_img in enumerate(os.listdir(os.path.join(img_path, 'mobile'))):
            data.append(
                {
                    'type': 'mobile',
                    'sort': str(i),
                    'img_url': '/static/homepage/mobile/' + mobile_img,
                }
            )
        response['status'] = 'success'
        response['errCode'] = None
        response['errMsg'] = None
        response['data'] = data
    except Exception as e:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Unknown Path.'
        response['data'] = None
        logging.debug('Catch an exception. Quikok/views get_banner_bar', exc_info=True)
    return JsonResponse(response)
