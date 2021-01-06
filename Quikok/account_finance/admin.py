from django.contrib import admin
from account_finance.models import student_remaining_minutes_of_each_purchased_lesson_set
from account_finance.models import student_purchase_record

# Register your models here.

class studentRemainingMinutesAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_time', 'last_changed_time')

class studentPurchaseRecordAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'update_time')

admin.site.register(
    student_remaining_minutes_of_each_purchased_lesson_set, 
    studentRemainingMinutesAdmin
)

admin.site.register(
    student_purchase_record, 
    studentPurchaseRecordAdmin
)
