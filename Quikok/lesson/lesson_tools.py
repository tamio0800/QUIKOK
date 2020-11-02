from account.models import teacher_profile, favorite_lessons
from lesson.models import lesson_info, lesson_reviews, lesson_card
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Avg, Sum  
# 上面兩個用來對資料庫的資訊做處理，用法如下(有null的話要另外處理)
# model_name.objects.filter().aggregate(Sum('column_name')) >> {'column_name__sum':?}
import pandas as pd
import os


def clean_files(folder_path, key_words):
    for each_file in os.listdir(folder_path):
        if key_words in each_file:
            os.unlink(os.path.join(folder_path, each_file))


def get_lesson_s_best_sale(lesson_id):
    lesson_object = lesson_info.objects.filter(id=lesson_id).first()
    trial_class_price = lesson_object.trial_class_price
    price_per_hour = lesson_object.price_per_hour
    if trial_class_price != -999 and trial_class_price < price_per_hour:
        # 有試教優惠的話就直接回傳
        return "試課優惠"
    else:
        discount_price = lesson_object.discount_price
        discount_pairs = discount_price.split(';')
        all_discounts = [int(_.split(':')[-1]) for _ in discount_pairs if len(_) > 0]
        if len(all_discounts) == 0:
            # 沒有折數
            return ''
        else:
            best_discount = min(all_discounts)
            return str(100 - best_discount) + '% off'
            # 反之則回傳  xx% off


class lesson_manager:
    def __init__(self):
        self.status = ''
        self.errCode = None
        self.errMsg = None
        self.data = dict()
    def return_lesson_details(self, lesson_id, user_auth_id, for_whom='common_users'):
        # for_whom接收的參數有兩個，'common_users' 以及 'teacher_who_created_it'
        if for_whom == 'common_users':
            # 給一般user看的，不需要特別檢查該user是否為本課程的創始人。
            lesson_object = lesson_info.objects.filter(id=lesson_id).first()
            if lesson_object is None:
                self.status = 'failed'
                self.errCode = 1
                self.errMsg = 'Found No Lesson.'
                return (self.status, self.errCode, self.errMsg, self.data)
        elif for_whom == 'teacher_who_created_it':
            # 在這裡for_whomfrom_whom指的是teacher's auth_id
            lesson_object = lesson_info.objects.filter(id=lesson_id).filter(teacher__auth_id=user_auth_id).first()
            if lesson_object is None:
                self.status = 'failed'
                self.errCode = 2
                self.errMsg = 'Found No Lesson OR Non Match User.'
                return (self.status, self.errCode, self.errMsg, self.data)        
        _data = self.fetch_lesson_details(lesson_id=lesson_id)
        self.status = 'success'
        self.errCode = None
        self.errMsg = None
        # 在下面定義API的回傳, 就是回傳資料加工區啦
        exclude_columns = [
            'id', 'teacher_id', 'created_time']      
        for each_col in _data.keys():
            if each_col not in exclude_columns:
                self.data[each_col] = _data[each_col]
        # 課程的資料加工完畢，來點開課老師本身的資訊
        self.data['is_this_teacher_male'] = \
            teacher_profile.objects.filter(id=lesson_object.teacher_id).first().is_male   
        # 如果for_whom == 'common_users'，要加上資訊: 這門課是不是該user的最愛?   
        # 以及該開課老師的auth_id
        if for_whom == 'common_users':
            this_user_favorite_lessons_object = favorite_lessons.objects.filter(follower_auth_id=user_auth_id)
            if this_user_favorite_lessons_object is None:
                self.data['is_this_my_favorite_lesson'] = False
            else:
                this_user_favorite_lessons_s_ids = this_user_favorite_lessons_object.values_list('lesson_id', flat=True)
                self.data['is_this_my_favorite_lesson'] = \
                    lesson_id in this_user_favorite_lessons_s_ids
                print(self.data)
            self.data['teacher_auth_id'] = \
                teacher_profile.objects.filter(id=lesson_object.teacher_id).first().auth_id
        else:
            # 是要給老師看的，另外加上for老師的資訊    
            self.data['best_sale'] = get_lesson_s_best_sale(lesson_id=lesson_id)  
        return (self.status, self.errCode, self.errMsg, self.data)
    def fetch_lesson_details(self, lesson_id):
        lesson_object = lesson_info.objects.filter(id = lesson_id)
        return lesson_object.values()[0]
    

    def setup_a_lesson(self, teacher_auth_id, a_request_object, lesson_id, action):
        # 全新的課程建立
        _temp_lesson_info = dict()
        exclude_columns = [
            'id', 'teacher', 'created_time', 
            'lesson_avg_score', 'lesson_reviewed_times', 'background_picture_path']
        columns_to_be_read = \
                [field.name for field in lesson_info._meta.get_fields() if field.name not in exclude_columns]
        
        for each_column_to_be_read in columns_to_be_read:
            _arg = a_request_object.POST.get(each_column_to_be_read, 'was_None')
            if _arg == 'was_None':
                self.status = 'failed'
                self.errCode = '0'
                self.errMsg = 'Connection Failed >> ' + each_column_to_be_read  + ' is None.'
                return (self.status, self.errCode, self.errMsg)
            else:
                _temp_lesson_info[each_column_to_be_read] = _arg
        _temp_lesson_info['lesson_has_one_hour_package'] = \
            _temp_lesson_info['lesson_has_one_hour_package'] == 'true'
        # 轉成boolean
        # if a_request_object.POST.get('unitClassPrice', False):
            # 代表其非為空值，且非為None
        #    _temp_lesson_info['lesson_has_one_hour_package'] = True
        _temp_lesson_info['teacher'] = teacher_profile.objects.filter(auth_id=teacher_auth_id).first()

        if action == 'createLesson':
            _temp_lesson_info['lesson_avg_score'] = 0
            _temp_lesson_info['lesson_reviewed_times'] = 0
            if _temp_lesson_info['teacher'] is None:
                self.status = 'failed'
                self.errCode = '2'
                self.errMsg = 'Found No Teacher.'
                return (self.status, self.errCode, self.errMsg)
            try:
                # 建立老師的lessons資料夾, 下方的lesson_id資料夾，如
                # user_uploaded/teachers/username/lessons/3(<< which is the lesson id)
                lessons_folder_path = \
                    'user_upload/teachers/' + _temp_lesson_info['teacher'].username + '/lessons'
                if not os.path.isdir(lessons_folder_path):
                    os.mkdir(lessons_folder_path)
                # 判斷老師是否有上傳圖片
                has_teacher_uploaded_lesson_background_picture = \
                    int(_temp_lesson_info['background_picture_code']) == 99
                _temp_lesson_info['background_picture_path'] = ''  # 因為還不知道lesson_id，故先給空字串
                created_lesson = lesson_info.objects.create(
                    **_temp_lesson_info
                )  # 建立課程檔案
                # created_lesson.save()
                lessons_folder_path = \
                    lessons_folder_path + '/' + str(created_lesson.id)
                if not os.path.isdir(lessons_folder_path):
                    os.mkdir(lessons_folder_path)
                if has_teacher_uploaded_lesson_background_picture:
                    # 有上傳圖片
                    uploaded_background_picture = a_request_object.FILES["background_picture_path"]
                    print('received bg pic: ', uploaded_background_picture.name)
                    fs = FileSystemStorage(location=lessons_folder_path)
                    file_extension = uploaded_background_picture.name.split('.')[-1]
                    fs.save('customized_lesson_background'+'.'+ file_extension , uploaded_background_picture) # 檔名統一改成thumbnail開頭
                    created_lesson.background_picture_path = \
                        '/' + lessons_folder_path + '/customized_lesson_background'+'.'+ file_extension
                created_lesson.save()
                the_lesson_card_manager = lesson_card_manager()
                the_lesson_card_manager.setup_a_lesson_card(
                    corresponding_lesson_id = created_lesson.id,
                    teacher_auth_id = teacher_auth_id
                )  # 建立課程小卡資訊

                self.status = 'success'
                self.errCode = None
                self.errMsg = None
                return (self.status, self.errCode, self.errMsg)
            except Exception as e:
                print(e)
                self.status = 'failed'
                self.errCode = '3'
                self.errMsg = 'Error While Writting In Database.'
                return (self.status, self.errCode, self.errMsg)
        
        elif action == 'editLesson':
            if _temp_lesson_info['teacher'] is None:
                self.status = 'failed'
                self.errCode = '2'
                self.errMsg = 'Found No Teacher.'
                return (self.status, self.errCode, self.errMsg)    
            try:
                edited_lesson = lesson_info.objects.filter(teacher__auth_id=teacher_auth_id).filter(id=lesson_id).first()
                if edited_lesson is None:
                    # 代表課程跟老師對應不起來
                    self.status = 'failed'
                    self.errCode = '2'
                    self.errMsg = 'Found No Matched Teacher And The Lesson.'
                    return (self.status, self.errCode, self.errMsg)
                # 建立老師的lessons資料夾 & 下方lesson_id資料夾(如果沒有建立的話)
                lessons_folder_path = \
                    'user_upload/teachers/' + _temp_lesson_info['teacher'].username + '/lessons' 
                if not os.path.isdir(lessons_folder_path):
                    os.mkdir(lessons_folder_path)
                lessons_folder_path = \
                    lessons_folder_path + '/' + str(edited_lesson.id) 
                if not os.path.isdir(lessons_folder_path):
                    os.mkdir(lessons_folder_path)
                # 判斷老師是否有上傳圖片
                has_teacher_uploaded_lesson_background_picture = \
                    int(_temp_lesson_info['background_picture_code']) == 99
                if has_teacher_uploaded_lesson_background_picture:
                    # 有上傳圖片
                    uploaded_background_picture = a_request_object.FILES["background_picture_path"]
                    print('received bg pic: ', uploaded_background_picture.name)
                    fs = FileSystemStorage(location=lessons_folder_path)
                    file_extension = uploaded_background_picture.name.split('.')[-1]
                    clean_files(lessons_folder_path, 'customized_lesson_background')  # 先清理過舊的背景圖片
                    fs.save('customized_lesson_background'+'.'+ file_extension , uploaded_background_picture) # 檔名統一改成thumbnail開頭
                    print('/' + lessons_folder_path + '/customized_lesson_background'+'.'+ file_extension)
                    _temp_lesson_info['background_picture_path'] = \
                        '/' + lessons_folder_path + '/customized_lesson_background'+'.'+ file_extension

                for key, item in _temp_lesson_info.items():
                    setattr(edited_lesson, key, item)
                edited_lesson.save()
                the_lesson_card_manager = lesson_card_manager()
                the_lesson_card_manager.setup_a_lesson_card(
                    corresponding_lesson_id = lesson_id,
                    teacher_auth_id = teacher_auth_id
                )  # 更新課程小卡資訊

                self.status = 'success'
                self.errCode = None
                self.errMsg = None
                return (self.status, self.errCode, self.errMsg)
            except Exception as e:
                print(e)
                self.status = 'failed'
                self.errCode = '3'
                self.errMsg = 'Error While Writting In Database.'
                return (self.status, self.errCode, self.errMsg)


class lesson_card_manager: 
    def __init__(self):
        self.lesson_card_info = dict()

    def setup_a_lesson_card(self, **kwargs):
        # 當課程建立或是修改時，同步編修課程小卡資料
        print("Activate setup_a_lesson_card!!!!")
        from account.models import teacher_profile
        from lesson.models import lesson_info, lesson_reviews, lesson_card
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
            self.lesson_card_info['best_sale'] = get_lesson_s_best_sale(kwargs['corresponding_lesson_id'])
        
            # 再取得老師資訊與評價資訊
            self.lesson_card_info['teacher_auth_id'] =  kwargs['teacher_auth_id']
            self.lesson_card_info['teacher_nickname'] =  teacher_object.nickname
            self.lesson_card_info['teacher_thumbnail_path'] =  teacher_object.thumbnail_dir
            self.lesson_card_info['is_this_teacher_male'] =  teacher_object.is_male
            
            self.lesson_card_info['education'] =  teacher_object.education_1
            self.lesson_card_info['education_is_approved'] =  teacher_object.education_approved
            self.lesson_card_info['working_experience'] =  teacher_object.company
            self.lesson_card_info['working_experience_is_approved'] =  teacher_object.work_approved
  
            if len(review_objects) == 0:
                # 這是一個新上架的課程或是沒有人給予過評論
                self.lesson_card_info['lesson_reviewed_times'] = 0
                self.lesson_card_info['lesson_avg_score'] = 0
            else:
                self.lesson_card_info['lesson_reviewed_times'] = len(review_objects)
                self.lesson_card_info['lesson_avg_score'] = review_objects.aggregate(_avg = Avg('score_given'))['_avg']
            
            # 先確認這個課程小卡是否存在，不存在的話建立，存在的話修改
            lesson_card_object = lesson_card.objects.filter(corresponding_lesson_id=self.lesson_card_info['corresponding_lesson_id']).first()
            if lesson_card_object is None:
                #  建立
                lesson_card.objects.create(
                    **self.lesson_card_info
                ).save()
            else:
                #  修改
                self.lesson_card_info.pop('corresponding_lesson_id', None)
                for key, item in self.lesson_card_info.items():
                    setattr(lesson_card_object, key, item)
                lesson_card_object.save()
            return True
        except Exception as e:
            print('setup lesson card error:  ', e)
            return False
    
    


