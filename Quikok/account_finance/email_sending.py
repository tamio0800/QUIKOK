from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info
from blog.models import article_info
from django.template.loader import render_to_string
from django.utils.html import strip_tags
#from account_finance.email_sending import email_manager
class email_manager:
    def email_content(self, num):
        pass
    
    def system_msg_new_order_payment_remind(self, **kwargs):
        #data_test = {'studentID':7, 'teacherID':1,'lessonID':1,'lesson_set':'test' ,'price':100}
        
        try:
            price = kwargs['price']                
            student_authID = kwargs['studentID']
            teacher_authID = kwargs['teacherID']
            lesson_id = kwargs['lessonID']
            lesson_set = kwargs['lesson_set']

            student_info = student_profile.objects.filter(auth_id = student_authID).first()
            student_email_address = student_info.username
            teacher_info = teacher_profile.objects.filter(auth_id = teacher_authID).first() 
            teacher_name = teacher_info.nickname
            lesson_title = lesson_info.objects.filter(id = lesson_id).first().lesson_title
            
            email_body = article_info.objects.filter(id=1).first().content
    
            email = EmailMessage(
                subject = '訂課匯款提醒',  # 電子郵件標題
                body = strip_tags(email_body),
                #body = '您好！QUIKOK!開課收到您選購了'+ teacher_name + '老師的',
                from_email= settings.EMAIL_HOST_USER,  # 寄件者
                to =  ['colorfulday0123@gmail.com']# 先用測試用的信箱[student_email_address]  # 收件者
            )
            email.fail_silently = False
            email.send()

            return True
        except Exception as e:
            print(f'Exception: {e}')
            return False

    def send_email(self, **kwargs):
        subject = kwargs['subject']
        body = kwargs['body']
        to_whom = kwargs['to_whom']

        email = EmailMessage(
            subject = '測試信',  # 電子郵件標題
            body = '測試看看能不能真的發出去的內容',
            from_email=settings.EMAIL_HOST_USER,  # 寄件者
            to = ['tamio.chou@gmail.com']  # 收件者
        )
        email.fail_silently = False
        email.send()