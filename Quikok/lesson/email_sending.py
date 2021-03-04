from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string, get_template
from account.models import teacher_profile, student_profile
# from lesson.models import lesson_info, lesson_sales_sets
# from blog.models import article_info
# from django.template import Context, Template
# import asyncio
# from lesson.models import lesson_info
import os
from django.conf import settings
from time import time
#from django.utils.html import strip_tags
#from email.mime.image import MIMEImage 夾附件用
#from account_finance.email_sending import email_manager


class lesson_email_manager:
    #print(os.getcwd())
    # 管理email標題以及要渲染的html
    def __init__(self):
        self.email_pattern = {
            '通知學生要確認上課時數': os.path.join(settings.BASE_DIR,'student_send_complete_course.html'),
            '提醒老師要評價學生': os.path.join(settings.BASE_DIR,'teacher_send_complete_course.html'),
            '提醒老師明天要上課': os.path.join(settings.BASE_DIR, 'lesson/templates/lesson/send_remind_class.html'),
            '提醒學生明天要上課': os.path.join(settings.BASE_DIR,  'lesson/templates/lesson/send_remind_class.html'),
            '提醒學生老師對他的預約有回覆(婉拒或接受)': os.path.join(settings.BASE_DIR, 'lesson/templates/lesson/student_send_order_reply.html'),
            '提醒學生跟老師有人取消預約':os.path.join(settings.BASE_DIR, 'lesson/templates/lesson/send_cancel_booking.html'),
        
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
                
                if settings.DISABLED_EMAIL == False:
                    email = EmailMessage(
                        subject = '[副本]Quikok!開課通知：老師請你確認上課時數囉!',  # 電子郵件標題
                        body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                        from_email= settings.EMAIL_HOST_USER,  # 寄件者
                        to =  ['quikok.taiwan@quikok.com']#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                    ) # 正式發布時要改為 to student_email
                    email.fail_silently = False
                    email.content_subtype = 'html'
                    email.send()

                    if settings.DEV_MODE == False:
                        # 生產環境要寄送email給用戶
                        email = EmailMessage(
                            subject = 'Quikok!開課通知：老師請你確認上課時數囉!',  # 電子郵件標題
                            body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                            from_email= settings.EMAIL_HOST_USER,  # 寄件者
                            to =  [student_email]#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                        ) # 正式發布時要改為 to student_email
                        email.fail_silently = False
                        email.content_subtype = 'html'
                        email.send()


                return True

            except Exception as e:
                print(f'send_student_confirm_time_when_teacher_completed_lesson Exception: {e}')
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
                
                if settings.DISABLED_EMAIL == False:
                    email = EmailMessage(
                        subject = '[副本]Quikok!開課通知：給學生的評價填了嗎~',  # 電子郵件標題
                        body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                        from_email= settings.EMAIL_HOST_USER,  # 寄件者
                        to =  ['quikok.taiwan@quikok.com']#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                    ) # 正式發布時要改為 to teacher_email
                    email.fail_silently = False
                    email.content_subtype = 'html'
                    email.send()

                    if settings.DEV_MODE == False:
                        email = EmailMessage(
                            subject = 'Quikok!開課通知：給學生的評價填了嗎~',  # 電子郵件標題
                            body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                            from_email= settings.EMAIL_HOST_USER,  # 寄件者
                            to =  [teacher_email]#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                        ) # 正式發布時要改為 to teacher_email
                        email.fail_silently = False
                        email.content_subtype = 'html'
                        email.send()

                return True

            except Exception as e:
                print(f'send_teacher_rate_student_when_teacher_completed_lesson Exception: {e}')
                return False
        else:
            print('缺少參數')
            return False

    def send_student_remind_one_day_before_lesson(self, **kwargs):
        # 信件主題:提醒學生明天要上課
        # 預約時間的前一天寄信提醒
        st = time()
        student_authID = kwargs['student_authID']
        lesson_title = kwargs['lesson_title']
        booking_date_and_time = kwargs['booking_date_and_time']
        if student_authID :
            #try:
            pattern_html = self.email_pattern['提醒學生明天要上課']
            suit_pattern = get_template(pattern_html)
            student_obj = student_profile.objects.get(auth_id=student_authID)
            user_nickname = student_obj.nickname
            student_email = student_obj.username
            
            email_context = {
                'user_nickname':user_nickname,
                'lesson_title': lesson_title,
                'booking_date_and_time':booking_date_and_time
            }
            email_body = suit_pattern.render(email_context)
            
            if settings.DISABLED_EMAIL == False:
                email = EmailMessage(
                    subject = '[副本]Quikok!開課提醒：明天要上課唷',  # 電子郵件標題
                    body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                    from_email= settings.EMAIL_HOST_USER,  # 寄件者
                    to =  ['quikok.taiwan@quikok.com']#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                ) # 正式發布時要改為 to student_email
                email.fail_silently = False
                email.content_subtype = 'html'
                email.send()

                if settings.DEV_MODE == False:
                    email = EmailMessage(
                        subject = 'Quikok!開課提醒：明天要上課唷',  # 電子郵件標題
                        body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                        from_email= settings.EMAIL_HOST_USER,  # 寄件者
                        to =  [student_email]#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                    ) # 正式發布時要改為 to student_email
                    email.fail_silently = False
                    email.content_subtype = 'html'
                    email.send()

            return True

        else:
            print('缺少參數')
            return False

    def send_teacher_remind_one_day_before_lesson(self, **kwargs):
        # 信件主題:提醒老師明天要上課
        # 預約時間的前一天寄信提醒
        lesson_title = kwargs['lesson_title']
        booking_date_and_time = kwargs['booking_date_and_time']      
        teacher_authID = kwargs['teacher_authID']
        
        if teacher_authID :
            try:
                pattern_html = self.email_pattern['提醒老師明天要上課']
                suit_pattern = get_template(pattern_html)
                teacher_obj = teacher_profile.objects.get(auth_id=teacher_authID)
                teacher_nickname = teacher_obj.nickname
                teacher_email = teacher_obj.username
                
                email_context = {
                    'user_nickname':teacher_nickname ,
                    'lesson_title': booking_date_and_time,
                    'booking_date_and_time':lesson_title
                }
                email_body = suit_pattern.render(email_context)

                if settings.DISABLED_EMAIL == False:
                    email = EmailMessage(
                        subject = '[副本]Quikok!開課提醒：明天要上課唷',  # 電子郵件標題
                        body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                        from_email= settings.EMAIL_HOST_USER,  # 寄件者
                        to =  ['quikok.taiwan@quikok.com']#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                    ) # 正式發布時要改為 to teacher_email
                    email.fail_silently = False
                    email.content_subtype = 'html'
                    email.send()

                    if settings.DEV_MODE == False:
                        email = EmailMessage(
                            subject = 'Quikok!開課提醒：明天要上課唷',  # 電子郵件標題
                            body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                            from_email= settings.EMAIL_HOST_USER,  # 寄件者
                            to =  [teacher_email]#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                        ) # 正式發布時要改為 to teacher_email
                        email.fail_silently = False
                        email.content_subtype = 'html'
                        email.send()

                return True

            except Exception as e:
                print(f'send_teacher_remind_one_day_before_lesson Exception: {e}')
                return False
        else:
            print('缺少參數')
            return False

    def send_student_and_teacher_someone_canceld_the_booking(self, **kwargs):
        # 信件主題:提醒學生跟老師有人取消預約
        user_nickname = kwargs['user_nickname']
        user_email_address = kwargs['user_email_address']
        lesson_title = kwargs['lesson_title']
        
        if user_nickname and user_email_address and lesson_title :
            #try:
            pattern_html = self.email_pattern['提醒學生跟老師有人取消預約']
            suit_pattern = get_template(pattern_html)
            
            email_context = {
                'user_nickname': user_nickname,
                'lesson_title': lesson_title,
            }
            email_body = suit_pattern.render(email_context)
            
            if settings.DISABLED_EMAIL == False:
                email = EmailMessage(
                    subject = '[副本]Quikok!開課提醒：預約取消提醒！',  # 電子郵件標題
                    body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                    from_email= settings.EMAIL_HOST_USER,  # 寄件者
                    to =  ['quikok.taiwan@quikok.com']#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                ) # 正式發布時要改為 to user_email_address
                email.fail_silently = False
                email.content_subtype = 'html'
                email.send()
            
                if settings.DEV_MODE == False:
                    email = EmailMessage(
                        subject = 'Quikok!開課提醒：預約取消提醒！',  # 電子郵件標題
                        body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                        from_email= settings.EMAIL_HOST_USER,  # 寄件者
                        to =  [user_email_address]#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                    ) # 正式發布時要改為 to user_email_address
                    email.fail_silently = False
                    email.content_subtype = 'html'
                    email.send()
            
            return True

            
        else:
            print('缺少參數')
            return False
    
    def send_student_remind_teacher_responded_the_booking(self, **kwargs):
        # 信件主題:提醒學生老師拒絕或是接受他的預約
        # (請他重新預約時間或與老師聯繫後再預約)
        #st = time()
        student_authID = kwargs['student_authID']
        teacher_nickname = kwargs['teacher_nickname']
        lesson_title = kwargs['lesson_title']
        
        if student_authID and teacher_nickname and lesson_title :
            #try:
            pattern_html = self.email_pattern['提醒學生老師對他的預約有回覆(婉拒或接受)']
            suit_pattern = get_template(pattern_html)
            student_obj = student_profile.objects.get(auth_id=student_authID)
            
            student_nickname = student_obj.nickname
            student_email = student_obj.username
            
            email_context = {
                'student_nickname':student_nickname,
                'teacher_nickname':teacher_nickname,
                'lesson_title': lesson_title,
            }
            email_body = suit_pattern.render(email_context)

            if settings.DISABLED_EMAIL == False:
                email = EmailMessage(
                    subject = 'Quikok!開課提醒：老師回覆預約邀請了！',  # 電子郵件標題
                    body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                    from_email= settings.EMAIL_HOST_USER,  # 寄件者
                    to =  ['quikok.taiwan@quikok.com']#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                ) # 正式發布時要改為 to student_email
                #print(f"lesson/email_sending, EmailMessage consumed time test: {time()-st}")
                email.fail_silently = False
                email.content_subtype = 'html'
                email.send()

                if settings.DEV_MODE == False:
                    email = EmailMessage(
                        subject = 'Quikok!開課提醒：老師回覆預約邀請了！',  # 電子郵件標題
                        body = email_body, #strip_tags(email_body), #這寫法可以直接把HTML TAG去掉並呈現HTML的排版
                        from_email= settings.EMAIL_HOST_USER,  # 寄件者
                        to =  [student_email]#,'colorfulday0123@gmail.com','w2003x3@gmail.com','mimigood411@gmail.com', 'tamio.chou@gmail.com'] #先用測試用的信箱[student_email_address]  # 收件者
                    ) # 正式發布時要改為 to student_email
                    #print(f"lesson/email_sending, EmailMessage consumed time test: {time()-st}")
                    email.fail_silently = False
                    email.content_subtype = 'html'
                    email.send()
            return True
  
        else:
            print('缺少參數')
            return False