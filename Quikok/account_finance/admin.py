from django.contrib import admin
from account_finance.models import (student_remaining_minutes_of_each_purchased_lesson_set,
                    student_purchase_record,student_refund, teacher_refund,
                    user_purchase_exam_bank_record)
        

# Register your models here.
class userPurchaseExamBankRecordAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_time', 'updated_time')

class studentRemainingMinutesAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_time', 'last_changed_time')

class studentPurchaseRecordAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'updated_time')


class studentRefundAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'student_auth_id', 'snapshot_balance', 'created_time', 'update_time')


class teacherRefundAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'teacher_auth_id', 'snapshot_balance', 'created_time', 'update_time')

admin.site.register(
    user_purchase_exam_bank_record,
    userPurchaseExamBankRecordAdmin
)
admin.site.register(
    student_remaining_minutes_of_each_purchased_lesson_set, 
    studentRemainingMinutesAdmin
)

admin.site.register(
    student_purchase_record, 
    studentPurchaseRecordAdmin
)

admin.site.register(student_refund, studentRefundAdmin)
admin.site.register(teacher_refund, teacherRefundAdmin)
