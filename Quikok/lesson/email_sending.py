from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string, get_template
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info, lesson_sales_sets
from blog.models import article_info
from django.template import Context, Template
import asyncio
from lesson.models import lesson_info
#from django.utils.html import strip_tags
#from email.mime.image import MIMEImage 夾附件用
#from account_finance.email_sending import email_manager
class email_manager:

    # 管理email標題以及要渲染的html
    def __init__(self):
        self.email_pattern = {
            '通知學生要確認上課時數': './student_send_complete_course.html',
            '提醒老師要評價學生': './teacher_send_complete_course.html'
        }
    def send_student_confirm_time_when_teacher_completed_lesson(self, **kwargs):
        # 信件主題:通知學生要確認上課時數
        # 當有老師送出完課、填寫時數後要提醒學生確認時間
        
        student_authID = kwargs['student_authID']
        if student_authID :
            try:
                pattern_html = self.email_pattern['通知學生要確認上課時數']
                suit_pattern = get_template(pattern_html)
                student_obj = student_profile.objects.get(auth_id=student_authID)
                student_nickname = student_obj.nickname
                student_email = student_obj.username
                
                email_context = {
                    'student_nickname':student_nickname
                }
                email_body = suit_pattern.render(email_context)
                email = EmailMessage(
                    subject = 'Quikok!開課通知：老師請你確認上課時數囉!',  # 電子郵件標題
                    body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                    from_email= settings.EMAIL_HOST_USER,  # 寄件者
                    to =  ['quikok.taiwan@quikok.com']#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                ) # 正式發布時要改為 to student_email
                email.fail_silently = False
                email.content_subtype = 'html'
                email.send()
                return True

            except Exception as e:
                print(f'Exception: {e}')
                return False
        else:
            print('缺少參數')
            return False
    
    def send_teacher_rate_student_when_teacher_completed_lesson(self, **kwargs):
        # 信件主題:通知學生要確認上課時數
        # 當有老師送出完課、填寫時數後要提醒學生確認時間
        
        teacher_authID = kwargs['teacher_authID']
        if teacher_authID :
            try:
                pattern_html = self.email_pattern['提醒老師要評價學生']
                suit_pattern = get_template(pattern_html)
                teacher_obj = teacher_profile.objects.get(auth_id=teacher_authID)
                teacher_nickname = teacher_obj.nickname
                teacher_email = teacher_obj.username
                
                email_context = {
                    'teacher_nickname':teacher_nickname
                }
                email_body = suit_pattern.render(email_context)
                email = EmailMessage(
                    subject = 'Quikok!開課通知：給學生的評價填了嗎~',  # 電子郵件標題
                    body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                    from_email= settings.EMAIL_HOST_USER,  # 寄件者
                    to =  ['quikok.taiwan@quikok.com']#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                ) # 正式發布時要改為 to teacher_email
                email.fail_silently = False
                email.content_subtype = 'html'
                email.send()
                return True

            except Exception as e:
                print(f'Exception: {e}')
                return False
        else:
            print('缺少參數')
            return False
