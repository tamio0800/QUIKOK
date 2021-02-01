from django.contrib import admin
from account.models import student_profile, teacher_profile
from account.models import student_review_aggregated_info, teacher_review_aggregated_info

# Register your models here.


class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'auth_id', 'date_join')

class TeacherAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'auth_id', 'all_lesson_score_mean', 'total_number_of_remark', 'date_join')


class StudentAggregatedReviewsAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'student_auth_id', 'score_given_sum', 'reviewed_times', 'receiving_review_lesson_minutes_sum',
    'is_student_late_for_lesson_times', 'is_student_frivolous_in_lesson_times', 'is_student_or_parents_not_friendly_times', 
    'last_updated_time']

class TeacherAggregatedReviewsAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'teacher_auth_id', 'score_given_sum', 'reviewed_times', 'receiving_review_lesson_minutes_sum',
    'is_teacher_late_for_lesson_times', 'is_teacher_frivolous_in_lesson_times', 'is_teacher_incapable_times', 
    'last_updated_time']


admin.site.register(student_profile, StudentAdmin)
admin.site.register(teacher_profile, TeacherAdmin)
admin.site.register(student_review_aggregated_info, StudentAggregatedReviewsAdmin)
admin.site.register(teacher_review_aggregated_info, TeacherAggregatedReviewsAdmin)

