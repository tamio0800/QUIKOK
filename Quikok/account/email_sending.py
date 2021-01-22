from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template #render_to_string, 
#from django.template import Context, Template
#from django.utils.html import strip_tags
#from email.mime.image import MIMEImage 夾附件用
#from account_finance.email_sending import email_manager
class email_manager:

    # 管理emai主題以及要渲染的html
    def __init__(self):
        self.email_pattern = {
            '學生註冊成功通知': './student_send_sign_up_success.html',
            '老師註冊成功通知': './teacher_send_sign_up_success.html'
        }
    
    def send_welcome_email_new_signup_teacher(self, **kwargs):
        teacher_authID = kwargs['teacher_authID']
        teacher_nickname = kwargs['teacher_nickname']
        teacher_email = kwargs['teacher_email']
        #e.send_welcome_email_new_signup_teacher(teacher_authID = 1,teacher_nickname = 'test', teacher_email =  'test')
        if False not in [teacher_authID,teacher_nickname,teacher_email]:
            try:
                pattern_html = self.email_pattern['老師註冊成功通知']
                suit_pattern = get_template(pattern_html)
                email_context = {
                    'teacher_nickname': teacher_nickname
                }
                email_body = suit_pattern.render(email_context)

                email = EmailMessage(
                    subject = 'Quikok!開課 註冊成功通知',  # 電子郵件標題
                    body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                    from_email= settings.EMAIL_HOST_USER,  # 寄件者
                    to =  ['colorfulday0123@gmail.com']#,'w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                ) # 正式發布時要改為 to teacher_email
                email.fail_silently = False
                email.content_subtype = 'html'
                email.send()

                return True
            except Exception as e:
                print(f'Exception: {e}')
                return False
    
    def send_welcome_email_new_signup_student(self, **kwargs):
        student_authID = kwargs['student_authID']
        student_nickname = kwargs['student_nickname']
        student_email = kwargs['student_email']
        #e.send_welcome_email_new_signup_student(student_authID = 1,student_nickname = 'test',student_email =  'test')
        if False not in [student_authID,student_nickname,student_email]:
            try:
                pattern_html = self.email_pattern['老師註冊成功通知']
                suit_pattern = get_template(pattern_html)
                email_context = {
                    'student_nickname': student_nickname
                }
                email_body = suit_pattern.render(email_context)

                email = EmailMessage(
                    subject = 'Quikok!開課 註冊成功通知',  # 電子郵件標題
                    body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                    from_email= settings.EMAIL_HOST_USER,  # 寄件者
                    to =  ['colorfulday0123@gmail.com']#,'w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                ) # student_email
                email.fail_silently = False
                email.content_subtype = 'html'
                email.send()

                return True
            except Exception as e:
                print(f'Exception: {e}')
                return False