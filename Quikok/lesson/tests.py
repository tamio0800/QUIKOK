from django.test import TestCase
import pandas as pd
import os
from lesson.models import lesson_info
from account.models import teacher_profile

# 將課程批次匯入db中的
df_lesson = pd.read_excel('test_folder/批次匯入課程.xlsx')

for each_row_num in range(df_lesson.shape[0]):
    #print(each_row)
    teacher_id = teacher_profile.objects.get(id = each_row_num+1) #ForeignKey
    lesson_info.objects.create(
    lesson_id = df_lesson['lesson_id'][each_row_num],
    teacher = teacher_id,
    lesson_title = df_lesson['lesson_title'][each_row_num],
    price_per_hour = df_lesson['price_per_hour'][each_row_num],
    highlight_1 = df_lesson['highlight_1'][each_row_num],
    highlight_2 = df_lesson['highlight_2'][each_row_num],
    highlight_3 = df_lesson['highlight_3'][each_row_num],
    lesson_intro = df_lesson['lesson_intro'][each_row_num],
    how_does_lesson_go = df_lesson['how_does_lesson_go'][each_row_num],
    lesson_remarks = df_lesson['lesson_remarks'][each_row_num],
    lesson_picture_folder = '',
    syllabus = df_lesson['syllabus'][each_row_num],
    lesson_appendix_folder ='',
    lesson_attributes =df_lesson['lesson_attributes'][each_row_num],
    lesson_avg_score = 0,
    lesson_reviewed_times = 0,
    ).save()
