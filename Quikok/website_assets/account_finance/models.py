from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from account_finance.email_sending import email_manager
#from account_finance.email_machine import email_tools

# 購買題庫的紀錄
class user_purchase_exam_bank_record(models.Model):
    user_auth_id = models.IntegerField() # 購買者的 authID
    exam_bank_sales_set_id = models.IntegerField()
    start_date =  models.DateTimeField()  # 可使用題庫的有效時間開始日期，應為確認付款日
    end_date = models.DateTimeField() # 可使用題庫的有效時間結束日期
    is_valid = models.BooleanField(default=False) 
    #是否可使用題庫，在可使用題庫的有效期內即為有效，測試期間有效期開始日統一決定，
    # 不做是否在有效期間判定
    price = models.IntegerField() # total
    purchased_with_money  = models.IntegerField() # 實際要支付的費用 total_price -purchased_with_q_points
    purchased_with_q_points = models.IntegerField(default=0)  # 用多少Q幣支付,這版暫不會用到
    part_of_bank_account_code = models.CharField(max_length=30, default='')#銀行末5碼
    is_refunded = models.BooleanField(default=False) # 是否有退款,相關功能暫人工處理
    is_preorder = models.BooleanField(default=False) # 是否為預購期間購買
    created_time = models.DateTimeField(auto_now_add=True) 
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"題庫購買人auth_id: {str(self.user_auth_id)}, 方案:{str(self.exam_bank_sales_set_id)}"

    class Meta:
        verbose_name = '題庫訂閱紀錄'
        verbose_name_plural = '題庫訂閱紀錄'
        ordering = ['-updated_time']

# 學生購買紀錄
class student_purchase_record(models.Model):
    student_auth_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()
    teacher_nickname = models.CharField(max_length = 40)
    purchase_date = models.DateTimeField() 
    # 下訂日期, 原則上= created_time
    payment_deadline = models.DateTimeField() 
    #繳費期限=下訂日期+3天,到第三天的00:00
    lesson_id = models.IntegerField()
    lesson_title = models.CharField(max_length = 30)
    lesson_sales_set_id = models.IntegerField()
    price = models.IntegerField() # total
    purchased_with_q_points = models.IntegerField(default=0)  # 用多少Q幣支付
    purchased_with_money = models.IntegerField() # 實際要支付的費用 total_price -purchased_with_q_points
    part_of_bank_account_code = models.CharField(max_length=30, default='') 
    # 用戶繳費帳號後5碼,對帳用
    payment_status = models.CharField(max_length = 30, default = 'unpaid')
    # unpaid, reconciliation, paid, refunding, refunded, cancel_after_paid , unpaid_cancel
    # 0-待付款/1-對帳中/2-已付款/3-退款中/4-已退款/5-有付款_取消訂單 6. 未付款_取消訂單 
    # 1.15 依照設計畫的流程目前不會有3,5,已付款的按退款就會變成Q幣、變成已退款
    # 5是先留著,以免未來有需要
    # 取消指的是 把未付款的課程退掉；退款指的是把已經有付款的轉成Q幣
    updated_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"學生{str(self.student_auth_id)} 購買 {self.teacher_nickname} 總價 {str(self.price)} 的方案。 狀態: {self.payment_status}"

    class Meta:
        verbose_name = '學生購買紀錄'
        verbose_name_plural = '學生購買紀錄'
        ordering = ['-updated_time']


# 學生退款紀錄
class student_refund(models.Model):
    '''
    Qpoint轉換成台幣的退款
    '''
    student_auth_id = models.IntegerField()
    snapshot_balance = models.IntegerField(default=0) # 該次申請時的帳戶餘額
    txn_fee = models.IntegerField(default=0) # 手續費
    refund_amount = models.IntegerField() # 學生要退多少錢
    created_time = models.DateTimeField(auto_now_add=True)
    refund_status = models.CharField(max_length = 30, default = 'unpaid')
    # already_paid, unpaid, cancel...
    update_time = models.DateTimeField(auto_now=True)
    bank_account_code = models.CharField(max_length=30, default='')
    bank_name = models.CharField(max_length=30, default='')
    bank_code = models.CharField(max_length=5, default='')
    
    def __str__(self):
        return f"學生 {str(self.student_auth_id)} 退款 {str(self.refund_amount)} 元，手續費 {str(self.txn_fee)}。 狀態: {self.refund_status}"
    
    class Meta:
        verbose_name = '學生退款紀錄(退款用)'
        verbose_name_plural = '學生退款紀錄(退款用)'


# 老師提款紀錄(預設系統每個月自動轉帳
class teacher_refund(models.Model):
    teacher_auth_id = models.IntegerField()
    snapshot_balance = models.IntegerField(default=0) # 該次匯款給老師時的帳戶餘額
    txn_fee = models.IntegerField(default=0) # 手續費
    refund_amount = models.IntegerField() # 匯款多少錢,正常情況下是全額
    created_time = models.DateTimeField(auto_now_add=True)
    refund_status = models.CharField(max_length=30, default='unpaid')
    # paid, unpaid, cancel.....
    update_time = models.DateTimeField(auto_now=True)
    bank_account_code = models.CharField(max_length=30, default='')
    bank_name = models.CharField(max_length=30, default='')
    bank_code = models.CharField(max_length=5, default='')
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = '老師提款紀錄(退款用)'
        verbose_name_plural = '老師提款紀錄(退款用)'


class student_remaining_minutes_of_each_purchased_lesson_set(models.Model):
    student_purchase_record_id = models.IntegerField(default=0)
    # lesson_booking_info_ids = models.CharField(default='', max_length=20)
    # 對應的 lesson_booking_info id 們
    # 之所以 default = '' ，因為這樣子在我先前寫的測試中(不會用到這個欄位)就不會有一大堆衝突了QQ
    # 下面 copy 寫在 lesson_booking_info 那邊的註釋
    # 因為一則購買的方案可以用來做很多預約（多對一），
    # 反之方案快用完的時候也可能兩三個購買方案才能用來做一次大量預約（一對多），
    # 所以這裡使用 string 來做儲存，會長得類似： "9,10,11" or "3" 這樣子，
    # 當要 query 對應的 queryset 時可以這樣做  
    # student_remaining_minutes_of_each_purchased_lesson_set_ids 先簡寫為 srm_ids
    #   1. 
    #         for each_id in lesson_booking_info.objects.filter(id=1).srm_ids.split(','):
    #            student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(id=each_id)
    #            ...
    #  <<<<<>>>>> OR <<<<<>>>>>
    #   2.
    #         student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
    #               id__in = lesson_booking_info.objects.filter(id=1).srm_ids.split(',')
    #         )
    student_auth_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()  # 開課的老師 auth_id
    lesson_id = models.IntegerField()  # 所對應的課程id
    lesson_sales_set_id = models.IntegerField()  # 對應的方案id
    available_remaining_minutes = models.IntegerField()  # 可動用的剩餘時數
    withholding_minutes = models.IntegerField(default=0) # 預扣時數
    # to_be_confirmed_consumed_minutes = models.IntegerField(default=0) 
    # 01.11,經過討論暫時用不到這個欄位:待確認的上課時數
    confirmed_consumed_minutes = models.IntegerField(default=0)  
    # 已確認的上課時數,還沒確認的都會在預扣時數
    created_time = models.DateTimeField(auto_now_add=True)
    last_changed_time = models.DateTimeField(auto_now=True)
    is_refunded = models.BooleanField(default=False)
    # 代表學生有沒有退費這門方案，並且成功通過退費。

    def __str__(self):
        return f"學生auth_id: {str(self.student_auth_id)} >> 課程:{str(self.lesson_id)}, 方案:{str(self.lesson_sales_set_id)}, 可用時數:{str(self.available_remaining_minutes)}, 預扣時數:{str(self.withholding_minutes)}, 已用時數:{str(self.confirmed_consumed_minutes)}" 
    # 時數的名詞解釋範例:
    # 假設我買了100小時的課 已經上完30小時,其中28小時已經確認上完課,
    # 2小時老師跟學生雙方還在確認,實際上那堂課上了3小時
    # 並且另外預約了6小時, 老師還沒確認是否要接受預約.
    # 可動用的剩餘 available_remaining_minutes = 70*60
    # withholding_minutes = 6*60 ,當老師確認預約後,這個就會跑到待確認(下面)
    # 已確認預約未上課會跟已確認預約尚未確認完課的都算在be_confirmed
    # to_be_confirmed_consumed_minutes=2*60
    # confirmed_consumed_minutes=28*60
    # 當確認完課的時候, lesson_complete_record 的check_time=3*60
    # ?? 可是如果老師確認預約,這時候的be_confirmed = (6+2)*60
    # ?? 我要怎麼知道 -3 就是 2 那堂預約呢
    # 透過lesson_complete_record的lesson_booking_info_id
    # lesson_booking_info裡面有booking_date_and_time
    # 這邊會寫這堂預約我約兩小時

    class Meta:
        #ordering= ['-last_changed_time']  # 越新的會被呈現在越上面
        verbose_name = '學生課程方案剩餘時數'
        verbose_name_plural = '學生課程方案剩餘時數'
        


class student_owing_teacher_time(models.Model):
    '''
    這個表用來儲存，當課程超時的話，先扣除原先 withholding 的部份，然後再趁機從學生多的 available 扣除，
    但若學生沒有多的 available 可以扣，則先儲存在這邊，留待日後處理。
    '''
    student_auth_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()
    lesson_id = models.IntegerField()  # 所對應的課程id
    lesson_booking_info_id = models.IntegerField()  # 對應的預約id
    owing_minutes = models.PositiveIntegerField()  # 積欠的時數
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{str(self.student_auth_id)} owing {str(self.teacher_auth_id)} {str(self.owing_minutes)} minutes.' 

    class Meta:
        ordering= ['-created_time']  # 越新的會被呈現在越上面
        verbose_name = '學生積欠時數'
        verbose_name_plural = '學生積欠時數'


class student_remaining_minutes_when_request_refund_each_purchased_lesson_set(models.Model):
    '''
    時間轉Q幣用。
    當學生申請訂單退款時,當下剩餘的時間跟換算後的Q幣金額會儲存在這
    預計將來要處理"同一筆訂單分次退款"時也會用到
    '''
    student_purchase_record_id = models.IntegerField(default=0)
    purchased_lesson_sales_sets_id = models.IntegerField(default=0)  # 對應的 lesson_sales_sets id    
    snapshot_available_remaining_minutes = models.IntegerField()  # 可動用的剩餘時數
    snapshot_withholding_minutes = models.IntegerField(default=0) # 預扣時數
    available_minutes_turn_into_q_points = models.IntegerField(default=0) #時間轉Q幣的計算結果
    created_time = models.DateTimeField(auto_now_add=True)
    last_changed_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '學生訂單退款換算Q幣'
        verbose_name_plural = '學生訂單退款換算Q幣'


@receiver(pre_save, sender=student_purchase_record)
def on_change(sender, instance:student_purchase_record, **kwargs):
    if instance.id is None:
        pass  # 建立新資料不需要做什麼事情
    else:
        previous = student_purchase_record.objects.get(id=instance.id)
        if previous.payment_status == 'reconciliation' and instance.payment_status == 'paid' :
            from lesson.models import lesson_sales_sets
            # 代表確認付完款了
            # 現在要看看究竟買了多少時數
            the_sales_set = \
                lesson_sales_sets.objects.get(id=instance.lesson_sales_set_id).sales_set
            if the_sales_set == 'trial':
                times_of_the_sales_set_in_minutes = 30
            elif the_sales_set == 'no_discount':
                times_of_the_sales_set_in_minutes = 60
            else:
                # 長得類似 \d+:\d+
                times_of_the_sales_set_in_minutes = \
                    int(the_sales_set.split(':')[0]) * 60
        
            student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
                student_purchase_record_id = previous.id,
                student_auth_id = instance.student_auth_id,
                teacher_auth_id = instance.teacher_auth_id,
                lesson_id = instance.lesson_id,
                lesson_sales_set_id = instance.lesson_sales_set_id,
                available_remaining_minutes = times_of_the_sales_set_in_minutes
            ).save()
            
            # 如果有用q幣,更改學生的q幣額度及預扣額度
            if previous.purchased_with_q_points != 0 :
                update_student_balance = email_manager()
                update_student_balance.edit_student_balance_after_receive_payment(
                    student_authID = previous.student_auth_id,
                    q_discount = previous.purchased_with_q_points)
            
            else:
                pass # db不需要更新
            
            # 寄給學生收到款項提醒email
            lesson_set_name =  lesson_sales_sets.objects.filter(id = previous.lesson_sales_set_id).first().sales_set
            send_email_reminder = email_manager()
            send_email_data = {
                'email_pattern_name':'收到款項提醒',
                'total_lesson_set_price': previous.price,
                'studentID': previous.student_auth_id,
                'teacherID': previous.teacher_auth_id,
                'lessonID': previous.lesson_id,
                'lesson_set':lesson_set_name,
                'q_discount':previous.purchased_with_q_points
            }
            send_email_reminder.system_email_new_order_and_payment_remind(**send_email_data)

            # 寄信告訴老師有學生買他的課程
            #send_email = email_tools()
            send_email_reminder.send_teacher_when_student_buy_his_lesson(
                teacher_authID= previous.teacher_auth_id,
                student_authID = previous.student_auth_id,
                lesson_set=lesson_set_name,
                price = previous.price,
                lesson_title=previous.lesson_title,
                #teacher_nickname='TEST',
                #teacher_email='TEST',
                #student_nickname='TEST',
            )