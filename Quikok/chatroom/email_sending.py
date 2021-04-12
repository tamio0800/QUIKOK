from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string, get_template
from account.models import teacher_profile, student_profile
import os
from django.conf import settings
from time import time

        
# 這邊是給我們自己的email，有些情況我們會需要提醒自己
class chatroom_email_for_edony:
    def edony_unread_user_msg(self,unread_msg):
        '''每天檢查一次,提醒我們有未讀的訊息要上去看'''
        
        if settings.DISABLED_EMAIL == False:
            email = EmailMessage(
                subject = '球雀聊天室有未讀訊息',  # 電子郵件標題
                body = f'聊天室有：{unread_msg}則未讀訊息，請上線查看',
                from_email=settings.EMAIL_HOST_USER,  # 寄件者
                to = ['quikok.taiwan@quikok.com']  # 收件者
            )
            email.fail_silently = False
            email.send()