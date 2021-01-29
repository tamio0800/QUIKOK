from django.contrib import admin
from account.models import student_profile, teacher_profile

# Register your models here.


class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'auth_id', 'date_join')

class TeacherAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'auth_id', 'all_lesson_score_mean', 'total_number_of_remark', 'date_join')


admin.site.register(student_profile, StudentAdmin)
admin.site.register(teacher_profile, TeacherAdmin)
