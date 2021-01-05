from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from account_finance.email_sending import email_manager

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
    price = models.IntegerField() # total
    purchased_with_q_points = models.IntegerField(default=0)  # 用Q幣支付
    purchased_with_money = models.IntegerField() # 實際要支付的費用 total_price -purchased_with_q_points
    part_of_bank_account_code = models.CharField(max_length=30, default='') 
    # 用戶繳費帳號後5碼,對帳用
    payment_status = models.CharField(max_length = 30, default = 'unpaid')
    # paid, unpaid, cancel.....
    update_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = '學生購買紀錄'
        verbose_name_plural = '學生購買紀錄'

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
    bank_account_code = models.CharField(max_length=30, default='')
    bank_code = models.CharField(max_length=5, default='')
    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = '學生退款紀錄'
        verbose_name_plural = '學生退款紀錄'

# 老師提款紀錄(預設系統每個月自動轉帳
class teacher_refund(models.Model):
    teacher_auth_id = models.IntegerField()
    snapshot_balance = models.IntegerField(default=0) # 該次匯款給老師時的帳戶餘額
    txn_fee = models.IntegerField(default=0) # 手續費
    refund_amount = models.IntegerField() # 匯款多少錢,正常情況下是全額
    created_time = models.DateTimeField(auto_now_add=True)
    refund_status = models.CharField(max_length=30, default='unpaid')
    # paid, unpaid, cancel.....
    update_time = models.DateTimeField(auto_now_add=True)
    bank_account_code = models.CharField(max_length=30, default='')
    bank_code = models.CharField(max_length=5, default='')
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = '老師提款紀錄'
        verbose_name_plural = '老師提款紀錄'


class student_remaining_minutes_of_each_purchased_lesson_set(models.Model):
    student_auth_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()  # 開課的老師 auth_id
    lesson_id = models.IntegerField()  # 所對應的課程id
    lesson_set_id = models.IntegerField()  # 對應的方案id
    available_remaining_minutes = models.IntegerField()  # 可動用的剩餘時數
    withholding_minutes = models.IntegerField(default=0) # 預扣時數
    created_time = models.DateTimeField(auto_now_add=True)
    last_changed_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        #ordering= ['-last_changed_time']  # 越新的會被呈現在越上面
        verbose_name = '學生課程方案剩餘時數'
        verbose_name_plural = '學生課程方案剩餘時數'



@receiver(pre_save, sender=student_purchase_record)
def on_change(sender, instance:student_purchase_record, **kwargs):
    if instance.id is None:
        pass  # 建立新資料不需要做什麼事情
    else:
        previous = student_purchase_record.objects.get(id=instance.id)
        if previous.payment_status == 'unpaid' and instance.payment_status == 'paid' :

            from lesson.models import lesson_sales_sets
            # 代表確認付完款了
            # 現在要看看究竟買了多少時數
            the_sales_set = \
                lesson_sales_sets.objects.get(id=instance.lesson_set_id).sales_set
            
            if the_sales_set in ('trial', 'no_discount'):
                times_of_the_sales_set_in_minutes = 60
            else:
                # 長得類似 \d+:\d+
                times_of_the_sales_set_in_minutes = \
                    int(the_sales_set.split(':')[0]) * 60

            student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
                student_auth_id = instance.student_auth_id,
                teacher_auth_id = instance.teacher_auth_id,
                lesson_id = instance.lesson_id,
                lesson_set_id = instance.lesson_set_id,
                available_remaining_minutes = times_of_the_sales_set_in_minutes
            )
            send_email_reminder = email_manager()
            send_email_data = {
                'email_pattern_name':'收到款項提醒',
                'total_lesson_set_price':previous.price,
                'studentID':previous.student_auth_id,
                'teacherID':previous.teacher_auth_id,
                'lessonID': previous.lesson_id,
                'lesson_set':previous.lesson_set_id,
                'q_discount':previous.purchased_with_q_points
            }
            send_email_reminder.system_email_new_order_and_payment_remind(**send_email_data)

