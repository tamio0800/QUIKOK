from account.models import teacher_profile
from django.contrib.auth.models import User
import pandas as pd
import os

class lesson_manager:
    def __init__(self):
        pass # ?
    
    def create_lesson(self, **kwargs):
        response = {}
        #lesson_id = '某個規則'
        
        teacher_id = kwargs['teacher']
        big_title = kwargs['big_title']
        little_title= kwargs['little_title']
        
        default_background_picture= kwargs['default_background_picture']
        background_picture= kwargs['background_picture']
        lesson_title = kwargs['lesson_title']
        price_per_hour= kwargs['price_per_hour']
        highlight_1 = kwargs['highlight_1']
        highlight_2 = kwargs['highlight_2']
        highlight_3 = kwargs['highlight_3']
        lesson_intro = kwargs['lesson_intro']
        how_does_lesson_go = kwargs['how_does_lesson_go']
        target_students = kwargs['target_students']
        syllabus = kwargs['syllabus']
        lesson_remarks = kwargs['lesson_remarks']
        lesson_attributes = kwargs['lesson_attributes']

        lesson_info(
        lesson_id = lesson_id, 
        teacher = teacher_id,
        big_title = big_title,
        little_title= little_title,
        default_background_picture= default_background_picture,
        background_picture = background_picture,
        lesson_title = lesson_title,
        price_per_hour= price_per_hour,
        highlight_1 = highlight_1,
        highlight_2 = highlight_2,
        highlight_3 = highlight_3,
        lesson_intro = lesson_intro,
        how_does_lesson_go = how_does_lesson_go,
        target_students = target_students,
        syllabus = syllabus,
        lesson_remarks = lesson_remarks,
        lesson_attributes=  lesson_attributes,
        ).save()

    #def show_lesson_info():

    #def edit_lesson()
