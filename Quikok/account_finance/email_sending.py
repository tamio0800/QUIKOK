from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string, get_template
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info, lesson_sales_sets
# from blog.models import article_info
# from django.template import Context, Template
# import threading
import os
# import asyncio
from lesson.models import lesson_info
from time import time
#from django.utils.html import strip_tags
#from email.mime.image import MIMEImage 夾附件用
#from account_finance.email_sending import email_manager
class email_manager:
    #print(os.getcwd())
    # 管理email標題以及要渲染的html
    def __init__(self):
        self.email_pattern = {
            '訂課匯款提醒': './send_new_order_remind.html',
            '收到款項提醒': './send_order_success.html',
            '通知老師有學生購買他的課': './teacher_send_order_success.html',
            '通知老師有學生預約':'./teacher_send_remind_order.html'
        }
    def edit_student_balance_after_receive_payment(self, **kwargs):
        #print(os.getcwd())
        q_discount = kwargs['q_discount']
        studentID = kwargs['student_authID'] 
        student_info_obj = student_profile.objects.get(auth_id=studentID)

        student_info_obj.withholding_balance = student_info_obj.withholding_balance - q_discount
        #student_info_obj.balance = student_info_obj.balance - q_discount
        student_info_obj.save()

    # 寄給學生:收到訂單與收到匯款
    def system_email_new_order_and_payment_remind(self, **kwargs):
    #data_test = {'q_discount':20,'studentID':7, 'teacherID':1,'lessonID':1,'lesson_set':'30:70' ,'total_lesson_set_price':100,'email_pattern_name':'訂課匯款提醒'}
        try:
            email_pattern_name = kwargs['email_pattern_name']
            try:
                pattern_html = self.email_pattern[email_pattern_name]
            except:
                return False

            price = kwargs['total_lesson_set_price']                
            student_authID = kwargs['studentID']
            teacher_authID = kwargs['teacherID']
            lesson_id = kwargs['lessonID']
            lesson_set = kwargs['lesson_set']
            q_discount = kwargs['q_discount']

            student_info = student_profile.objects.filter(auth_id = student_authID).first()
            student_email_address = student_info.username
            teacher_info = teacher_profile.objects.filter(auth_id = teacher_authID).first() 
            teacher_name = teacher_info.nickname
            lesson_title = lesson_info.objects.filter(id = lesson_id).first().lesson_title
            #lesson_set = lesson_sales_sets.objects.get(id = lesson_set_id).sales_set
            #print(lesson_set)
            # 選擇方案的文字
            if lesson_set == 'trial':
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
                lesson_set_name = f'總時數：{set_amount_hour}小時，優惠：{set_discount}折'

            # Q幣折抵的文字
            if q_discount in ('0',0):
                q_discount_msg = '0（沒有使用Q幣折抵）'
                purchasing_price = price
            else:
                q_discount_msg = f'已折抵 {q_discount} 元'
                purchasing_price = int(price) - int(q_discount)
            #email_body = article_info.objects.filter(id=1).first().content 直接從資料庫取,難以做變數
            suit_pattern = get_template(pattern_html)
            
            email_context = {
                'user_nickname': student_info.nickname,
                'teacher_nickname': teacher_info.nickname,
                'price':price,
                'lesson_title':lesson_title,
                'lesson_set':lesson_set_name,
                'q_discount' :q_discount_msg,
                'purchasing_price':purchasing_price
            }
            email_body = suit_pattern.render(email_context)

            email = EmailMessage(
                subject = email_pattern_name,  # 電子郵件標題
                body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                from_email= settings.EMAIL_HOST_USER,  # 寄件者
                to =  ['quikok.taiwan@quikok.com']#,'w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
            )
            email.fail_silently = False
            email.content_subtype = 'html'
            email.send()

            return True
        except Exception as e:
            print(f'Exception is: {e}')
            return False

    def send_teacher_when_student_buy_his_lesson(self, **kwargs):
        # 信件主題:通知老師有學生購買他的課
        # 當有學生買老師的課、經過我們對帳確認後,會寄出這封信
        st = time()
        teacher_authID = kwargs['teacher_authID']
        student_authID = kwargs['student_authID']
        #teacher_nickname = kwargs['teacher_nickname'] 
        #teacher_email = kwargs['teacher_email'] #寄件對象
        lesson_title = kwargs['lesson_title']
        #student_nickname = kwargs['student_nickname']
        lesson_set = kwargs['lesson_set']
        price = kwargs['price'] # 該課程總額

        #e.send_send_teacher_when_student_buy_his_lesson(teacher_authID = 1,teacher_nickname = 'test', teacher_email =  'test')
        if False not in [teacher_authID, student_authID, price,
                            lesson_title, lesson_set]:
            try:
                pattern_html = self.email_pattern['通知老師有學生購買他的課']
                suit_pattern = get_template(pattern_html)
                #lesson_set = lesson_sales_sets.objects.get(id = lesson_set_id).sales_set
            
                # 選擇方案的文字
                if lesson_set == 'trial':
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
                    lesson_set_name = f'總時數：{set_amount_hour}小時，優惠：{set_discount}折'

                teacher_obj = teacher_profile.objects.get(auth_id=teacher_authID)
                teacher_nickname = teacher_obj.nickname
                student_nickname = student_profile.objects.get(auth_id=student_authID).nickname
                teacher_email = teacher_obj.username
                
                email_context = {
                    'teacher_nickname': teacher_nickname, 
                    'lesson_title':lesson_title,
                    'student_nickname':student_nickname,
                    'lesson_set':lesson_set_name,
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
                print(f"only account_finance class consumed time test: {time()-st}")
            
                return True
            except Exception as e:
                print(f'Exception: {e}')
                return False

    def send_teacher_when_student_booking_his_lesson(self, **kwargs):
        # 信件主題:通知老師有學生預約
        # 當有學生預約老師上課時間、我們要通知老師確認時間
        
        teacher_authID = kwargs['teacher_authID']
        student_authID = kwargs['student_authID']
        lesson_id = kwargs['lesson_id']

        if False not in [teacher_authID, student_authID, lesson_id]:
            try:
                pattern_html = self.email_pattern['通知老師有學生預約']
                suit_pattern = get_template(pattern_html)

                
                teacher_obj = teacher_profile.objects.get(auth_id=teacher_authID)
                teacher_nickname = teacher_obj.nickname
                student_nickname = student_profile.objects.get(auth_id=student_authID).nickname
                teacher_email = teacher_obj.username
                lesson_title = lesson_info.objects.get(id = lesson_id).lesson_title
                email_context = {
                    'teacher_nickname': teacher_nickname, 
                    'lesson_title':lesson_title,
                    'student_nickname':student_nickname,
                    'lesson_title': lesson_title
                }
                email_body = suit_pattern.render(email_context)
                email = EmailMessage(
                    subject = 'Quikok!開課通知：有學生預約上課！',  # 電子郵件標題
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


# 這邊是給我們自己的email,有些情況我們會需要提醒自己
class email_for_edony:
    #提醒我們有學生匯款,要對帳
    def send_email_reconciliation_reminder(self, **kwargs):
        student_authID =  kwargs['student_authID']
        user5_bank_code =  kwargs['user5_bank_code']
        total_price =  kwargs['total_price']
        email = EmailMessage(
            subject = '學生匯款通知信',  # 電子郵件標題
            body = f'學生authID：{student_authID}已匯款，金額：{total_price}元，銀行帳號末五碼：{user5_bank_code}。請對帳',
            from_email=settings.EMAIL_HOST_USER,  # 寄件者
            to = ['quikok.taiwan@quikok.com']  # 收件者
        )
        email.fail_silently = False
        email.send()



#class EMAIL_MANAGER_WITH_THREAD(threading.Thread):
    '''
    利用多執行緒的方式來寄送Email，避免用戶等待 G-Mail 初始化過久。
    '''
#    def __init__(self, **kwargs):
#        print(f"kwargs in THREAD {kwargs}")
#        super().__init__()  # 繼承 Thread 類別的所有 init 元素
#        # self.notifications = kwargs['notifications']  # 下訂單時會用到
#        self.notifications = kwargs
#
#    def run(self):
#        mail_notification = email_manager()
#        mail_notification.system_email_new_order_and_payment_remind(self.notifications)

