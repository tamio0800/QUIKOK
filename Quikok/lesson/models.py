from django.db import models

def lesson(models.Model): # 0903架構還沒想完整先把確定有的東西填入
    lesson_title = models.CharField(max_length = 10)
    highlight_1 = models.CharField(max_length = 10)  # 亮點介紹，不要超過10個字元長
    highlight_2 = models.CharField(max_length = 10)  # 亮點介紹，不要超過10個字元長
    highlight_3 = models.CharField(max_length = 10)  # 亮點介紹，不要超過10個字元長