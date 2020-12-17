from django.shortcuts import render, HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

class email_manager:

    def send_email(self):
        email = EmailMessage(
            subject = '測試信',  # 電子郵件標題
            body = '測試看看能不能真的發出去的內容',
            from_email=settings.EMAIL_HOST_USER,  # 寄件者
            to = ['tamio.chou@gmail.com']  # 收件者
        )
        email.fail_silently = False
        email.send()