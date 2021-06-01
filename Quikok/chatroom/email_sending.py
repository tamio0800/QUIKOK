from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string, get_template
import os, logging
from django.conf import settings
from time import time

logger_chatroom = logging.getLogger('chatroom_info')
class chatroom_email_manager:
    '''管理聊天室要寄給user的通知信'''

    def __init__(self):
        # 管理emai主題以及要渲染的html
        self.email_pattern = {
            '學生聊天室未讀通知': os.path.join(settings.BASE_DIR,'chatroom/templates/chatroom/student_unread_messages.html'),
            '老師聊天室未讀通知': os.path.join(settings.BASE_DIR,'chatroom/templates/chatroom/teacher_unread_messages.html')
        }


    def email_student_chatroom_unread(self, **kwargs):
        '''提醒學生聊天室有未讀訊息'''
        user_authID = kwargs['student_authID']
        user_nickname = kwargs['student_nickname']
        user_email = kwargs['student_email']

        if False not in [user_authID, user_nickname, user_email]:
            try:
                pattern_html = self.email_pattern['學生聊天室未讀通知']
                suit_pattern = get_template(pattern_html)
                email_context = {
                    'user_nickname': user_nickname
                }
                email_body = suit_pattern.render(email_context)

                if settings.DISABLED_EMAIL == False:
                    email = EmailMessage(
                        subject = 'Quikok!開課 提醒您，聊天室有未讀訊息！',  # 電子郵件標題
                        body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                        from_email= settings.EMAIL_HOST_USER,  # 寄件者
                        to =  [user_email]  # 收件者　quikok.taiwan@quikok.com
                    ) 
                    email.fail_silently = False
                    email.content_subtype = 'html'
                    email.send()
                return True

            except Exception as e:
                logger_chatroom.error(f'chatroom/student_chatroom_unread Exception: {e}')
                return False
        else:
            logger_chatroom.error(f'chatroom/student_chatroom_unread: 信件因缺少參數未成功寄出')


    def email_teacher_chatroom_unread(self, **kwargs):
        '''提醒老師聊天室有未讀訊息'''
        user_authID = kwargs['teacher_authID']
        user_nickname = kwargs['teacher_nickname']
        user_email = kwargs['teacher_email']

        if False not in [user_authID, user_nickname, user_email]:
            
            try:
                pattern_html = self.email_pattern['老師聊天室未讀通知']
                
                suit_pattern = get_template(pattern_html)
                email_context = {
                    'user_nickname': user_nickname
                }
                email_body = suit_pattern.render(email_context)

                if settings.DISABLED_EMAIL == False:
                        #if settings.DEV_MODE == False:
                    email = EmailMessage(
                        subject = 'Quikok!開課 提醒您，聊天室有未讀訊息！',  # 電子郵件標題
                        body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                        from_email= settings.EMAIL_HOST_USER,  # 寄件者
                        to =  [user_email]  # 收件者　quikok.taiwan@quikok.com
                    ) 
                    email.fail_silently = False
                    email.content_subtype = 'html'
                    email.send()
                return True

            except Exception as e:
                logger_chatroom.error(f'chatroom/teacher_chatroom_unread Exception: {e}')
                return False
        else:
            logger_chatroom.error(f'chatroom/student_chatroom_unread: 信件因缺少參數未成功寄出')


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