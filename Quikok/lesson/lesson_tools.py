from account.models import teacher_profile
from lesson.models import lesson_info, lesson_reviews, lesson_card
from django.contrib.auth.models import User
from django.db.models import Avg, Sum  
# 上面兩個用來對資料庫的資訊做處理，用法如下(有null的話要另外處理)
# model_name.objects.filter().aggregate(Sum('column_name')) >> {'column_name__sum':?}
import pandas as pd
import os

class lesson_manager:
    def __init__(self):
        pass # ?
    
    def create_lesson(self, **kwargs):
        response = {}
        #lesson_id = '某個規則'
        
        auth_id = kwargs['AuthId'] #Auth的Id
        teacher_username = User.objects.get(id = 'auth_id').username
        #teacher_id = teacher_profile.objects.get(id = 'temp_id').username
        teacher = teacher_profile.objects.get(username = teacher_username)
        #ForeignKey
        big_title = kwargs['big_title']
        little_title= kwargs['little_title']
        default_background_picture= kwargs['default_background_picture']
        background_picture= kwargs['background_picture']
        lesson_title = kwargs['lesson_title']
        price_per_hour= kwargs['price_per_hour']
        trial_class_price = kwargs['trialClassPrice']  # 該門課程的試上鐘點費
        discount_price = kwargs['discountPrice']
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
        #lesson_id = lesson_id, 
        teacher = teacher, #ForeignKey
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


class lesson_card_manager: 
    def __init__(self):
        self.lesson_card_info = dict()

    
    def setup_a_lesson_card(self, **kwargs):
        # 當課程建立或是修改時，同步編修課程小卡資料
        try:
            teacher_object = teacher_profile.objects.filter(auth_id = kwargs['teacher_auth_id']).first()
            lesson_object = lesson_info.objects.filter(id = kwargs['corresponding_lesson_id']).first()
            review_objects = lesson_reviews.objects.filter(corresponding_lesson_id = kwargs['corresponding_lesson_id'])
            
            
            # 先取得課程本身的資訊
            self.lesson_card_info['corresponding_lesson_id'] =  kwargs['corresponding_lesson_id']
            self.lesson_card_info['big_title'] =  lesson_object.big_title
            self.lesson_card_info['little_title'] =  lesson_object.little_title
            self.lesson_card_info['title_color'] =  lesson_object.title_color
            self.lesson_card_info['background_picture_code'] =  lesson_object.background_picture_code
            self.lesson_card_info['background_picture_path'] =  lesson_object.background_picture_path
            self.lesson_card_info['price_per_hour'] =  lesson_object.price_per_hour
            self.lesson_card_info['lesson_title'] =  lesson_object.lesson_title
            self.lesson_card_info['highlight_1'] =  lesson_object.highlight_1
            self.lesson_card_info['highlight_2'] =  lesson_object.highlight_2
            self.lesson_card_info['highlight_3'] =  lesson_object.highlight_3
            
            # 再取得老師資訊與評價資訊
            self.lesson_card_info['teacher_auth_id'] =  kwargs['teacher_auth_id']
            self.lesson_card_info['teacher_nickname'] =  teacher_object.nickname
            self.lesson_card_info['education'] =  teacher_object.education_1
            self.lesson_card_info['education_is_approved'] =  teacher_object.education_approved
            self.lesson_card_info['working_experience'] =  teacher_object.company
            self.lesson_card_info['working_experience_is_approved'] =  teacher_object.work_approved
  
            if len(review_object) == 0:
                # 這是一個新上架的課程或是沒有人給予過評論
                self.lesson_card_info['lesson_reviewed_times'] = 0
                self.lesson_card_info['lesson_avg_score'] = 0
            else:
                self.lesson_card_info['lesson_reviewed_times'] = len(review_objects)
                self.lesson_card_info['lesson_avg_score'] = review_objects.aggregate(_sum = Sum('score_given'))['_sum']

            lesson_card.objects.create(
                self.lesson_card_info
            ).save()

            return True
        except:
            return False

