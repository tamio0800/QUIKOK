from account.models import teacher_profile, favorite_lessons
from lesson.models import lesson_info, lesson_reviews, lesson_card
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Avg, Sum  
# 上面兩個用來對資料庫的資訊做處理，用法如下(有null的話要另外處理)
# model_name.objects.filter().aggregate(Sum('column_name')) >> {'column_name__sum':?}
import pandas as pd
import os
import re

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
class sea_man:

    def __init__(self):
        self.delimiters = r' |,'   # 目前只有「空格」跟「,」

    def get_key_words(self, key_words):
        if type(key_words) is str:
            # split後轉成elements in a list
            key_words = re.split(self.delimiters, key_words)
        return key_words

    def a_is_in_b(self, key_words, target_texts):
        key_words = self.get_key_words(key_words)
        for each_key_word in key_words:
            if each_key_word in target_texts:
                return True
        return False

    def get_model_key_value_where_a_is_in_its_specific_columns(self, key_words, column_names_as_list, returned_key, the_model_objects):
        matched_key_value_in_model = list()
        model_object_values_as_dicts_in_list = the_model_objects.values()
        for each_dict in model_object_values_as_dicts_in_list:
            for each_column_name in column_names_as_list:
                if self.a_is_in_b(key_words, each_dict[each_column_name]):
                    matched_key_value_in_model.append(
                        each_dict[returned_key]
                    )
                    break
        return matched_key_value_in_model
class lesson_manager:
    def __init__(self):
        self.status = ''
        self.errCode = None
        self.errMsg = None
        self.data = dict()
        # 以下是指篩選條件共有哪一些種類
        self.filtered_subjects = self.get_filtered_subjects()
        self.filtered_target_students = self.get_filtered_target_students()
        self.filtered_times = self.get_filtered_times()
        self.filtered_time_index = self.get_filtered_time_mapping_index()
        self.filtered_tutoring_experience = self.get_filtered_tutoring_experience()
        # current打頭的是指目前的篩選條件
        self.current_filtered_subjects = None
        self.current_filtered_target_students = None
        self.current_filtered_times = None
        self.current_filtered_tutoring_experience = None
        self.current_filtered_price_per_hour = None
    def get_filtered_subjects(self):
        return {
            0: '英文',
            1: '數學',
            2: '物理',
            3: '化學',
            4: '留學相關',
            5: '語言檢定',
        }
    def get_filtered_target_students(self):
        return {
            0: '國小',
            1: '國中',
            2: '高中職',
            3: '大專院校',
            4: '社會人士',
        }
    def get_filtered_times(self):
        return {
            0: '早上',  # 0500 - 1100
            1: '上午',  # 0930 - 1300
            2: '中午',  # 1030 - 1430
            3: '下午',  # 1230 - 1830
            4: '晚上',  # 1700 - 2300
            5: '深夜',  # 2130 - 0530
        }
    def get_filtered_time_mapping_index(self):
        _list5 = [_ for _ in range(42, 48)]
        _list5.extend([_ for _ in range(11)])
        return {
            0: [_ for _ in range(10, 22)],
            1: [_ for _ in range(19, 26)],
            2: [_ for _ in range(21, 29)],
            3: [_ for _ in range(24, 37)],
            4: [_ for _ in range(34, 46)],
            5: _list5
        }
    def get_filtered_tutoring_experience(self):
        return {
            0: '1年以內',
            1: '1-3年',
            2: '3-5年',
            3: '5-10年',
            4: '10年以上',
        }

    def parse_filtered_conditions(self, filtered_by_in_string):
        # API: filtered_by >>  
        #   filtered_subjects:0,2,3;filtered_target_students:0,1,2;filtered_tutoring_experience:0,2;'filtered_price_per_hour:200,400 
        #  若沒有該篩選條件則不show出來，filtered_price_per_hour的部份先低後高，若只有一邊的話會以,high或是low,的形式做呈現。
        if len(filtered_by_in_string) == 0:
            # 沒有任何篩選條件
            return False
        else:
            for each_filtering in filtered_by_in_string.split(';'):
                if 'filtered_subjects' in each_filtering:
                    keys_in_list = each_filtering.split(':')[-1].split(',')
                    self.current_filtered_subjects = list()
                    for each_key_in_list in keys_in_list:
                        self.current_filtered_subjects.append(
                            self.filtered_subjects[int(each_key_in_list)]
                        )
                elif 'filtered_target_students' in each_filtering:
                    keys_in_list = each_filtering.split(':')[-1].split(',')
                    self.current_filtered_target_students = list()
                    for each_key_in_list in keys_in_list:
                        self.current_filtered_target_students.append(
                            self.filtered_target_students[int(each_key_in_list)]
                        )
                elif 'filtered_times' in each_filtering:
                    keys_in_list = each_filtering.split(':')[-1].split(',')
                    self.current_filtered_times = list()
                    for each_key_in_list in keys_in_list:
                        self.current_filtered_times.extend(
                            self.filtered_time_index[int(each_key_in_list)]
                        )
                    self.current_filtered_times = \
                        list(set(self.current_filtered_times))
                elif 'filtered_tutoring_experience' in each_filtering:
                    keys_in_list = each_filtering.split(':')[-1].split(',')
                    self.current_filtered_tutoring_experience = list()
                    for each_key_in_list in keys_in_list:
                        self.current_filtered_tutoring_experience.append(
                            self.filtered_tutoring_experience[int(each_key_in_list)]
                        )
                elif 'filtered_price_per_hour' in each_filtering:
                    keys_in_list = each_filtering.split(':')[-1].split(',')
                    min_func = lambda x: 0 if x == '' else int(x)
                    max_func = lambda x: 99999 if x == '' else int(x)
                    self.current_filtered_price_per_hour = \
                        (min_func(keys_in_list[0]), max_func(keys_in_list[1]))
            return True         

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
            'id', 'teacher_id', 'created_time', 'edited_time']      
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
            'id', 'teacher', 'created_time', 'edited_time',
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
            _temp_lesson_info['lesson_has_one_hour_package'] in ['true', True]
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
                try:
                    # 為了要知道user有沒有上傳新的圖片
                    # 當有上傳圖片時，a_request_object.FILES["background_picture_path"]不會是None，
                    # 但沒上傳圖片時，不會有"background_picture_path"這個參數存在於FILES中，
                    # 所以會發生錯誤，這時候我們就知道user沒有上傳圖片了。
                    if int(_temp_lesson_info['background_picture_code']) == 99 and \
                        a_request_object.FILES["background_picture_path"] is not None:
                        has_teacher_uploaded_lesson_background_picture = True
                    else:
                        has_teacher_uploaded_lesson_background_picture = False
                except:
                    has_teacher_uploaded_lesson_background_picture = False
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
    
    
    def setup_batch_lessons(self, teacher_auth_ids, nums_of_lesson):
        from account.models import teacher_profile
        import numpy as np
        txt = '與三部曲不同，《銀河修理員》說的不再是小情小愛，而是像銀河寬闊的愛。在亂世中的香港，聽起來有點隱隱作痛。「平安」二字，過去這 11 個月對過多少人講？面對千瘡百孔的生活，我們想身邊所愛安好，「平安」變成了最好的祈願。香港人由烽烽火火到疫症蔓延，微小的願望看似脆弱怯懦，但道出了我們對現實的無力。\
    即使歌詞裏也描述到「誰能望穿我這種堅壯非堅壯」，死頂而已。偏偏這種死頂就是最捨身的愛。而我最喜歡的是最後一段：臣亮言：先帝創業未半，而中道崩殂。今天下三分，益州疲弊，此誠危急存亡之秋也。然侍衛之臣，不懈於內；忠志之士，忘身於外者，蓋追先帝之殊遇，欲報之於陛下也。誠宜開張聖聽，以光先帝遺德，恢弘志士之氣；不宜妄自菲薄，引喻失義，以塞忠諫之路也。宮中府中，俱為一體，陟罰臧否，不宜異同。若有作姦犯科，及為忠善者，宜付有司，論其刑賞，以昭陛下平明之治，不宜篇私，使內外異法也。\
    第一次合作，黃偉文為 Dear Jane 帶來了《銀河修理員》，在這個壞透的世界，它正來得合時。本以為是一首溝女小情歌（當然看著 MV 男主角都有被迷倒一下，哈哈），但聽了幾次後有種被療癒的力量。無論經歷任何風霜，都總會一起逆風對抗。「跨宇宙又橫越洪荒」的守護，震撼之餘又帶浪漫。我們每個人都期待生命中，面對生活裡的煩惱，世界的不公，出現一位屬於自己的銀河修理員。祝你在亂流下平安。'
        txt = [_ for _ in txt]
        def get_text(txt_list, num=150):
            return ''.join(list(np.random.choice(txt_list, num, True)))
        # 全新的課程建立
        _temp_lesson_info = dict()
        for each_teacher_auth_id in teacher_auth_ids:
            class_nums = np.random.randint(1, 6)
            for each_class in range(class_nums):
                _temp_lesson_info['teacher'] = teacher_profile.objects.filter(auth_id = each_teacher_auth_id).first()
                print(_temp_lesson_info['teacher'].username, 'is building a class', each_class, 'for', class_nums)
                _temp_lesson_info['lesson_avg_score'] = 0
                _temp_lesson_info['lesson_reviewed_times'] = 0
                _temp_lesson_info['big_title'] = get_text(txt, np.random.randint(0, 11))
                _temp_lesson_info['little_title']  = get_text(txt, np.random.randint(0, 11))
                if np.random.rand() > 0.5:
                    _temp_lesson_info['title_color'] = '#ffffff'
                else:
                    _temp_lesson_info['title_color'] = '#000000'
                if np.random.rand() < 0.15:
                    _temp_lesson_info['background_picture_code'] = 1
                elif np.random.rand() < 0.3:
                    _temp_lesson_info['background_picture_code'] = 2
                elif np.random.rand() < 0.45:
                    _temp_lesson_info['background_picture_code'] = 3
                else:
                    _temp_lesson_info['background_picture_code'] = 99
                _temp_lesson_info['lesson_title'] = get_text(txt, np.random.randint(0, 15))
                _temp_lesson_info['price_per_hour'] = np.random.randint(0, 2601)
                _temp_lesson_info['lesson_has_one_hour_package'] = np.random.rand() > 0.1
                if np.random.rand() < 0.45:
                    _temp_lesson_info['trial_class_price']  = -1
                else:
                    _temp_lesson_info['trial_class_price'] = np.random.randint(0, 501)
                dice = np.random.rand()
                if dice < 0.3:
                    # 1 package
                    _temp_lesson_info['discount_price'] = str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100)) + ';'
                elif dice < 0.6:
                    _temp_lesson_info['discount_price'] = str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100)) + ';' + \
                        str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100)) + ';'
                elif dice < 0.9:
                    _temp_lesson_info['discount_price'] = str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100)) + ';' + \
                        str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100)) + ';' + \
                        str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100))
                elif _temp_lesson_info['lesson_has_one_hour_package']:
                    _temp_lesson_info['discount_price'] = ''
                else:
                    _temp_lesson_info['discount_price'] = str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100)) + ';' + \
                        str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100)) + ';' + \
                        str(np.random.randint(5, 50)) + ":" + \
                        str(np.random.randint(55, 100))
                _temp_lesson_info['highlight_1'], _temp_lesson_info['highlight_2'], _temp_lesson_info['highlight_3'] = \
                    get_text(txt, np.random.randint(0, 11)), get_text(txt, np.random.randint(0, 11)), get_text(txt, np.random.randint(0, 11))
                _temp_lesson_info['lesson_intro'] = get_text(txt, np.random.randint(20, 400))
                _temp_lesson_info['how_does_lesson_go'] = get_text(txt, np.random.randint(20, 200))
                _temp_lesson_info['target_students'] = get_text(txt, np.random.randint(20, 200))
                _temp_lesson_info['lesson_remarks']  = get_text(txt, np.random.randint(20, 200))
                _temp_lesson_info['syllabus'] = '<div class="area"><div class="chapter"><div>第1章</div><div></div></div><div class="subsection"><div>1-1</div><div></div></div></div>'
                _temp_lesson_info['lesson_attributes'] = \
                ' '.join(['#'+get_text(txt, np.random.randint(1, 11)) for _temp in range(np.random.randint(1, 11))])
                _temp_lesson_info['selling_status'] = np.random.choice([
                    'selling', 'notSelling', 'draft'
                ])
                lessons_folder_path = \
                    'user_upload/teachers/' + _temp_lesson_info['teacher'].username + '/lessons'
                if not os.path.isdir(lessons_folder_path):
                    os.mkdir(lessons_folder_path)
                _temp_lesson_info['background_picture_path'] = ''  # 因為還不知道lesson_id，故先給空字串
                created_lesson = lesson_info.objects.create(
                    **_temp_lesson_info
                )  # 建立課程檔案
                if _temp_lesson_info['background_picture_code'] == 99:
                    pic_path = 'account/batched_creating/lesson_background'
                    pic_name, pic_ext = np.random.choice(os.listdir(pic_path)).split('.')
                    _temp_lesson_info['background_picture_code'] = \
                        '/' + lessons_folder_path + '/customized_lesson_background'+'.'+ pic_ext
                    shutil.copy(
                        os.path.join(pic_path, pic_name + '.' + pic_ext),
                        _temp_lesson_info['background_picture_code'][1:]
                    )
                    created_lesson.background_picture_path = _temp_lesson_info['background_picture_code']
                created_lesson.save()
                the_lesson_card_manager = lesson_card_manager()
                the_lesson_card_manager.setup_a_lesson_card(
                    corresponding_lesson_id = created_lesson.id,
                    teacher_auth_id = each_teacher_auth_id
                )  # 建立課程小卡資訊
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
            
            if len(review_objects) == 0:
                # 這是一個新上架的課程或是沒有人給予過評論
                self.lesson_card_info['lesson_reviewed_times'] = 0
                self.lesson_card_info['lesson_avg_score'] = 0
            else:
                self.lesson_card_info['lesson_reviewed_times'] = len(review_objects)
                self.lesson_card_info['lesson_avg_score'] = review_objects.aggregate(_avg = Avg('score_given'))['_avg']
            
            self.lesson_card_info['working_experience'] =  teacher_object.company
            self.lesson_card_info['working_experience_is_approved'] =  teacher_object.work_approved
            
            # 呈現學歷與經歷，若經歷為空則第二個呈現次要學歷，若亦為空則呈現 其他經歷或特殊專長
            if teacher_object.company != '':
                self.lesson_card_info['working_experience'] =  teacher_object.company
                self.lesson_card_info['working_experience_is_approved'] =  teacher_object.work_approved
            elif teacher_object.education_2 != '':
                self.lesson_card_info['working_experience'] =  teacher_object.education_2
                self.lesson_card_info['working_experience_is_approved'] =  self.lesson_card_info['education_is_approved']
            elif teacher_object.special_exp != '':
                self.lesson_card_info['working_experience'] =  teacher_object.special_exp
                self.lesson_card_info['working_experience_is_approved'] =  teacher_object.other_approved


                
            
            
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
    def sort_lessons_id_by(self, lesson_ids, ordered_by):
        # lesson_ids as a list
        # ordered_by as a string 暫時是這樣
        # best_sales, reach_rate_asc, reach_rate_desc, price_per_hour_asc, price_per_hour_desc, lesson_scores_asc, lesson_scores_desc
        def ordered_by_best_sales(lesson_ids, ordered_by):
            # 先以評分的次數來當作熱門的指標
            _sorted_ids = \
                lesson_info.objects.filter(id__in = lesson_ids).order_by('-lesson_reviewed_times').values_list('id', flat=True)
            return _sorted_ids
        def ordered_by_reach_rate(lesson_ids, ordered_by):
            if ordered_by[-5:] == '_desc':
                return lesson_ids
            else:
                return lesson_ids
        def ordered_by_price_per_hour(lesson_ids, ordered_by):
            if ordered_by[-5:] == '_desc':
                _sorted_ids = \
                    lesson_info.objects.filter(id__in = lesson_ids).order_by('-price_per_hour').values_list('id', flat=True)
            else:
                _sorted_ids = \
                    lesson_info.objects.filter(id__in = lesson_ids).order_by('price_per_hour').values_list('id', flat=True)
            return _sorted_ids
        def ordered_by_lesson_scores(lesson_ids, ordered_by):
            if ordered_by[-5:] == '_desc':
                _sorted_ids = \
                    lesson_info.objects.filter(id__in = lesson_ids).order_by('-lesson_avg_score').values_list('id', flat=True)
            else:
                _sorted_ids = \
                    lesson_info.objects.filter(id__in = lesson_ids).order_by('lesson_avg_score').values_list('id', flat=True)
            return _sorted_ids
        sorting_methods = {
            'best_sales': ordered_by_best_sales,
            'reach_rate_asc': ordered_by_reach_rate,
            'reach_rate_desc': ordered_by_reach_rate,
            'price_per_hour_asc': ordered_by_price_per_hour,
            'price_per_hour_desc': ordered_by_price_per_hour,
            'lesson_scores_asc': ordered_by_lesson_scores,
            'lesson_scores_desc': ordered_by_lesson_scores,
        }
        return sorting_methods[ordered_by](lesson_ids, ordered_by)
    def return_lesson_cards_for_common_users(self, user_auth_id, lesson_ids_in_list):
        pass
    


