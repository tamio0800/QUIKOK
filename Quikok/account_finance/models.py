from django.db import models
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info

# 學生購買紀錄
class student_purchase_record(models.Model):
    student_auth_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()
    teacher_nickname = models.CharField(max_length = 40)
    purchase_date = models.DateTimeField(auto_now_add=True) 
    # 下訂日期, 原則上= created_time
    payment_deadline = models.DateTimeField(auto_now_add=True) 
    #繳費期限=下訂日期+3天,到第三天的00:00
    lesson_id = models.IntegerField()
    lesson_name = models.CharField(max_length = 30)
    lesson_set_id = models.IntegerField()
    price = models.IntegerField()
    bank_account_code = models.IntegerField() # 用戶繳費帳號後5碼,對帳用
    payment_status = models.CharField(max_length = 30, default = 'unpaid')
    # paid, unpaid, cancel.....
    update_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)

# 學生退款紀錄
class student_refund(models.Model):
    student_auth_id = models.IntegerField()
    snapshot_balance = models.IntegerField(default=0) # 該次申請時的帳戶餘額
    txn_fee = models.IntegerField(default=0) # 手續費
    refund_amount = models.IntegerField() # 學生要退多少錢
    created_time = models.DateTimeField(auto_now_add=True)
    refund_status = models.CharField(max_length = 30, default = 'unpaid')
    # already_paid, unpaid, cancel.....
    update_time = models.DateTimeField(auto_now_add=True)
    bank_account_code = models.CharField(max_length = 30)
    bank_code = models.CharField(max_length = 5)
    def __str__(self):
        return str(self.id)

# 老師提款紀錄(預設系統每個月自動轉帳
class teacher_refund(models.Model):
    teacher_auth_id = models.IntegerField()
    snapshot_balance = models.IntegerField(default=0) # 該次匯款給老師時的帳戶餘額
    txn_fee = models.IntegerField(default=0) # 手續費
    refund_amount = models.IntegerField() # 匯款多少錢,正常情況下是全額
    created_time = models.DateTimeField(auto_now_add=True)
    refund_status = models.CharField(max_length = 30, default = 'unpaid')
    # paid, unpaid, cancel.....
    update_time = models.DateTimeField(auto_now_add=True)
    bank_account_code = models.CharField(max_length = 30)
    bank_code = models.CharField(max_length = 5)
    def __str__(self):
        return str(self.id)