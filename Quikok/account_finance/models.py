from django.db import models
from account.models import teacher_profile, student_profile
# Create your models here.

class lesson_sales_sets(models.Model):
    lesson_id = models.CharField(max_length=20) 
    teacher_model = models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='teacher_of_the_lesson_snapshot')
    sales_set = models.CharField(max_length = 30)
    created_time = models.DateTimeField(auto_now_add = True)
    edited_time = models.DateTimeField(auto_now = True)
