from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string, get_template
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info
from blog.models import article_info
from django.template import Context, Template
from django.utils.html import strip_tags
#from email.mime.image import MIMEImage 夾附件用
#from account_finance.email_sending import email_manager
class email_manager:
    def email_content(self, num):
        pass
    def system_msg_new_order_payment_remind(self, **kwargs):
        #data_test = {'studentID':7, 'teacherID':1,'lessonID':1,'lesson_set':'30:70' ,'total_lesson_set_price':100}
        try:
            price = kwargs['total_lesson_set_price']                
            student_authID = kwargs['studentID']
            teacher_authID = kwargs['teacherID']
            lesson_id = kwargs['lessonID']
            lesson_set = kwargs['lesson_set']

            student_info = student_profile.objects.filter(auth_id = student_authID).first()
            student_email_address = student_info.username
            teacher_info = teacher_profile.objects.filter(auth_id = teacher_authID).first() 
            teacher_name = teacher_info.nickname
            lesson_title = lesson_info.objects.filter(id = lesson_id).first().lesson_title
            
            if lesson_set == 'trail':
                lesson_set_name = '試教課程'
            elif lesson_set == 'no_discount':
                lesson_set_name = '單堂課程'
            else:
                set_info = lesson_set.split(':')
                set_amount_hour = set_info[0]
                set_discount = set_info[1]
                
                if '0' in set_discount: # 70 折-> 7折
                    set_discount = set_discount.strip('0')
                else: # 75折-> 7.5折
                    set_discount = set_discount[0]+'.'+set_discount[1]

                lesson_set_name = f'總時數：{set_amount_hour}小時，優惠:{set_discount}折'

            #email_body = article_info.objects.filter(id=1).first().content 直接從資料庫取,難以做變數
            suit_pattern = get_template('./send_new_order_remind.html')
            
            email_context = {
                'user_nickname': student_info.nickname,
                'teacher_nickname': teacher_info.nickname,
                'price':price,
                'lesson_title':lesson_title,
                'lesson_set':lesson_set_name
            }
            email_body = suit_pattern.render(email_context)

            email = EmailMessage(
                subject = '訂課匯款提醒',  # 電子郵件標題
                body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                from_email= settings.EMAIL_HOST_USER,  # 寄件者
                to =  ['colorfulday0123@gmail.com', 'w2003x3@gmail.com']#'mimigood411@gmail.com' tamio.chou@gmail.com 先用測試用的信箱[student_email_address]  # 收件者
            )
            email.fail_silently = False
            email.content_subtype = 'html'
            email.send()

            return True
        except Exception as e:
            print(f'Exception: {e}')
            return False


# 這是一個最基本的寄信範例
    def send_email(self, **kwargs):
        email = EmailMessage(
            subject = '測試信',  # 電子郵件標題
            body = '測試看看能不能真的發出去的內容',
            from_email=settings.EMAIL_HOST_USER,  # 寄件者
            to = ['tamio.chou@gmail.com']  # 收件者
        )
        email.fail_silently = False
        email.send()