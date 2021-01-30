from django.contrib import admin
from lesson.models import * 
# Register your models here.

class LessonAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'teacher', 'created_time', 'edited_time')

class LessonForUserNotSignedUpAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_time')

class LessonBookingInfoAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'lesson_id', 'student_auth_id', 'teacher_auth_id', 'created_time', 'last_changed_time')

class LessonSalesSetAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id', 'lesson_id', 'teacher_auth_id',
        'selling_volume', 'taking_lesson_volume', 'fulfilled_volume',
         'created_time', 'last_sold_time')

class LessonCompletedAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id', 'lesson_booking_info_id', 'student_auth_id', 'teacher_auth_id',
        'created_time', 'last_changed_time')


admin.site.register(lesson_info, LessonAdmin)
admin.site.register(lesson_info_for_users_not_signed_up, LessonForUserNotSignedUpAdmin)
admin.site.register(lesson_booking_info, LessonBookingInfoAdmin)
admin.site.register(lesson_sales_sets, LessonSalesSetAdmin)
admin.site.register(lesson_completed_record, LessonCompletedAdmin)
