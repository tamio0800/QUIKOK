from account_finance.models import student_purchase_record, student_remaining_minutes_of_each_purchased_lesson_set
from account.models import teacher_profile
from account_finance.models import student_purchase_record 
from datetime import datetime, timedelta, date as date_function
from handy_functions import check_if_all_variables_are_true
from django.db.models.signals import pre_save
from django.dispatch import receiver, Signal
'''
用來測試是否可以監聽訂單狀態從paid變成unpaid並修改student_profile
'''
a_signal = Signal(providing_args=['a'])

class happy_test:
#    def test_re(sender, **kwargs):
#        a_signal.send(sender=student_purchase_record, a=1)

# 以下用法確定可以        
    new_order_paid_signal = Signal(providing_args=['a'])
    new_order_paid_signal.send(sender= student_purchase_record,a=1)

    @receiver(new_order_paid_signal)    
    def save_receive(sender, **kwargs):
        print('ya~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(kwargs)
    #test_re.connect(test_re, sender=student_purchase_record)