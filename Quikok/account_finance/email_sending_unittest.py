from django.test import TestCase
from time import time
# from account_finance.email_sending import email_manager
from django.core.mail import EmailMessage
from django.conf import settings

# python manage.py test account_finance.email_sending_unittest --settings=Quikok.settings_for_test

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
            to = ['tamio.chou@quikok.com']  # 收件者
        )
        email.fail_silently = False
        email.send()


class EMAIL_TEST(TestCase):

    def setUp(self):
        self.M = email_for_edony()
        self.start_time = time()

    def test_how_long_does_it_take_to_send_an_email(self):
        ret = self.M.send_email_reconciliation_reminder(
            student_authID=7, 
            user5_bank_code='11111', 
            total_price = 122 )
        print(f"測試成功: {ret}")
        print(f"耗時: {time()-self.start_time}")
