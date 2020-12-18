from django.db import models
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info
# Create your models here.

class student_purchase_record(models.Model):
    auth_id = models.IntegerField() 
    student_profile_id = models.ForeignKey(student_profile,on_delete=models.CASCADE, related_name='student_info')
    purchase_lesson_id = models.ForeignKey(lesson_info,on_delete=models.CASCADE, related_name='lesson_info')
    purchase_date = models.DateTimeField(auto_now_add=True)