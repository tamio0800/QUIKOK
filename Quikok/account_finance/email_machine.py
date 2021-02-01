from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template
from account.models import student_profile,teacher_profile

'''
class email_tools:

    # 管理emai主題以及要渲染的html
    def __init__(self):
        self.email_pattern = {
            '通知老師有學生購買他的課': './teacher_send_order_success.html'
        }
    
    
    def send_teacher_when_student_buy_his_lesson(self, **kwargs):
        # 信件主題:通知老師有學生購買他的課
        # 當有學生買老師的課、經過我們對帳確認後,會寄出這封信
        teacher_authID = kwargs['teacher_authID']
        teacher_nickname = kwargs['teacher_nickname'] 
        teacher_email = kwargs['teacher_email'] #寄件對象
        lesson_title = kwargs['lesson_title']
        student_nickname = kwargs['student_nickname']
        lesson_set = kwargs['lesson_set']
        price = kwargs['price'] # 該課程總額

        #e.send_send_teacher_when_student_buy_his_lesson(teacher_authID = 1,teacher_nickname = 'test', teacher_email =  'test')
        if False not in [teacher_authID,teacher_nickname,teacher_email,
                            lesson_title,student_nickname,lesson_set]:
            try:
                pattern_html = self.email_pattern['老師註冊成功通知']
                suit_pattern = get_template(pattern_html)
                email_context = {
                    'teacher_nickname': teacher_nickname,
                    'lesson_title':lesson_title,
                    'student_nickname':student_nickname,
                    'lesson_set':lesson_set,
                    'price':price
                }
                email_body = suit_pattern.render(email_context)

                email = EmailMessage(
                    subject = 'Quikok!開課通知：有學生購買您開設的課程',  # 電子郵件標題
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
'''