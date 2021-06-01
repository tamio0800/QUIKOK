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
    '''檢查我們是否有未讀、有的話寄信提醒，每間隔24小時執行一次, 只設定起始時間'''
    if settings.DISABLED_EMAIL == False:
        unread_msg = chat_history_Mr_Q2user.objects.filter(system_is_read = 0,user_is_read =1).count()
        if unread_msg != 0:
            chatroom_email_edony_notification.edony_unread_user_msg(unread_msg)
            logger_chatroom.info('chatroom 例行檢查，寄出未讀訊息')


# 以下是寄信給客人提醒的部分，將來或許可記錄寄信時間，
# 以免客人都不看聊天室系統卻每天寄信，徒增系統負擔
def check_if_teacher_chatroom_unread():
    '''檢查老師是否有未讀、有的話寄信提醒他，每間隔24小時執行一次, 只設定起始時間'''
    # 首先列出所有的老師
    if settings.DISABLED_EMAIL == False:
        all_teacher = teacher_profile.objects.all()
        for teacher in all_teacher:
            # 1,2,3,4,5 系統測試帳號, 正式機不用特別檢查聊天室
            if teacher.id not in [1,2,3,4,5]: 
                # 檢查是否有未讀訊息, 若有就寄信通知
                unread_msg = chat_history_user2user.objects.filter(teacher_auth_id = teacher.id ,teacher_is_read = 0).exists()
                if unread_msg :
                    logger_chatroom.info('chatroom 例行檢查老師有未讀訊息,發送email')
                    chatroom_user_notification.email_teacher_chatroom_unread(
                        teacher_authID = teacher.id,
                        teacher_nickname = teacher.nickname ,
                        teacher_email = teacher.username
                    )

def check_if_student_chatroom_unread():
    '''檢查老師是否有未讀、有的話寄信提醒他，每間隔24小時執行一次, 只設定起始時間'''
    # 首先列出所有的老師
    if settings.DISABLED_EMAIL == False:
        all_student = student_profile.objects.all()
        for student in all_student:
            # 6,7,9,10,11,36,76,79,80,82 系統測試帳號, 正式機不用特別檢查這幾個聊天室
            if student.id not in [6,7,9,10,11,36,76,79,80,82]: 
                # 檢查是否有未讀訊息, 若有就寄信通知
                unread_msg = chat_history_user2user.objects.filter(student_auth_id = student.id ,
                                                                    student_is_read = 0).exists()
                if unread_msg :
                    logger_chatroom.info('chatroom 例行檢查學生有未讀訊息,發送email')
                    print(student.id, student.nickname, student.username )
                    chatroom_user_notification.email_student_chatroom_unread(
                        student_authID = student.id,
                        student_nickname = student.nickname ,
                        student_email = student.username
                    )

# 寄給edony的每 8小時檢查
scheduler.add_job(check_if_edony_chatroom_unread, 'interval',
    hours = 8, start_date = '2021-04-12 01:00:00')
logger_chatroom.info('chatroom.view 例行檢查edony是否有未讀訊息')
    # hours = 24
   #,end_date = '2021-02-02 10:31:00' seconds, minutes, hours

# 寄給客人的每24小時檢查
scheduler.add_job(check_if_teacher_chatroom_unread, 'interval',
    hours = 24, start_date = '2021-04-12 11:00:00')
logger_chatroom.info('chatroom.view 例行檢查老師是否有未讀訊息')

scheduler.add_job(check_if_student_chatroom_unread, 'interval',
    hours = 24, start_date = '2021-04-12 11:00:00')
logger_chatroom.info('chatroom.view 例行檢查老師是否有未讀訊息')

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
