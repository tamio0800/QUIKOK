from django.db import models
from account.models import teacher_profile, student_profile

class lesson_info(models.Model): # 0903架構還沒想完整先把確定有的東西填入
    # 每堂課程會有自己的unique id，我們用這個來辨識、串連課程
    lesson_id = models.CharField(max_length=20) 
    teacher = models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='teacher_of_the_lesson')
    lesson_title = models.CharField(max_length = 10)  # 課程的名稱
    highlight_1 = models.CharField(max_length = 10)  # 亮點介紹1，不要超過10個字元長
    highlight_2 = models.CharField(max_length = 10)  # 亮點介紹2，不要超過10個字元長
    highlight_3 = models.CharField(max_length = 10)  # 亮點介紹3，不要超過10個字元長
    lesson_intro = models.CharField(blank=True, max_length=300)
    # 課程詳細介紹，不超過300長度
    lesson_picture_folder = models.CharField(max_length=60)
    # 如果課程有相關圖片，可以儲存在這個資料夾中
    lesson_appendix_folder = models.CharField(max_length=60)
    # 如果課程有相關附件，可以儲存在這個資料夾中

class lesson_reviews(models.Model):
    # 每堂課程會有自己的unique id，我們用這個來辨識、串連課程
    lesson_id = models.CharField(max_length=20)
    student = models.ForeignKey(student, )
    # 記得加上評分(1~5)
    # 加上評語(如果有的話)
    # 可以加上真的有上課的圖以資證明（學蝦皮） 




