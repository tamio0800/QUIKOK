from django.contrib.auth.models import User
import lesson
from django.contrib.auth.hashers import PBKDF2SHA1PasswordHasher
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from time import time
import os, shutil
from django.contrib.auth.models import User
from account.models import student_profile, teacher_profile, specific_available_time, general_available_time
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
from account.models import teacher_profile, favorite_lessons
from lesson.lesson_tools import *
from django.contrib.auth.decorators import login_required
from account.model_tools import *
from django.db.models import Q
from handy_functions import (check_if_all_variables_are_true, date_string_2_dateformat,
                            sort_dictionaries_in_a_list_by_specific_key, 
                            booking_date_time_to_minutes_and_cleansing,
                            turn_date_string_into_date_format, 
                            turn_first_datetime_string_into_time_format,
                            return_none_if_the_string_is_empty, bound_number_string)
from lesson.models import (lesson_info, lesson_card, lesson_info_for_users_not_signed_up,
                            lesson_sales_sets, lesson_booking_info, lesson_completed_record,
                            lesson_reviews_from_students, student_reviews_from_teachers)
from account_finance.models import (student_remaining_minutes_of_each_purchased_lesson_set,
                                    student_owing_teacher_time)
from django.db.models import Sum
from analytics.signals import object_accessed_signal
from analytics.utils import get_client_ip
from datetime import datetime, timedelta, date as date_function
from account_finance.email_sending import email_manager, email_for_edony
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.cache import cache
from .email_sending import lesson_email_manager

 ##課前提醒排程功能分隔線##


def send_email_one_day_before_booking_date():
    email_info_dict = dict()
    send_email = lesson_email_manager()
    #baseline_time = datetime.now()+timedelta(days=1) # 製作出明天的日期當基準
    baseline_time = datetime.now()+timedelta(days=5) # 測試用
    # 篩選出年月日跟基準相同的課程
    st = time()
    booking_lesson_queryset = lesson_booking_info.objects.filter(booking_status='confirmed', 
                                                                booking_start_datetime__date = baseline_time)
    print(len(booking_lesson_queryset))
    for each_class in booking_lesson_queryset:
        class_time_datetime = each_class.booking_start_datetime
        class_time_str = class_time_datetime.strftime('%Y-%m-%d %H:%M:%S')
        email_info_dict['booking_date_and_time'] = class_time_str
        lesson_obj = lesson_info.objects.get(id=each_class.lesson_id)
        email_info_dict['lesson_title'] = lesson_obj.lesson_title
        email_info_dict['teacher_authID'] =  each_class.teacher_auth_id
        email_info_dict['student_authID'] =  each_class.student_auth_id
        send_email.send_student_remind_one_day_before_lesson(**email_info_dict)
        send_email.send_teacher_remind_one_day_before_lesson(**email_info_dict)
    print(f"booking_lesson_query consumed time test: {time()-st}")
# 例項化
scheduler = BackgroundScheduler()
# 每間隔24小時執行一次, 要設定起始與結束時間
st = time()
scheduler.add_job(send_email_one_day_before_booking_date, 'interval',
    seconds = 30, start_date = '2021-02-01 10:30:00')
    #,end_date = '2021-02-02 10:31:00' seconds, minutes, hours
scheduler.start()
print(f"consumed time test: {time()-st}")
##課前提醒排程功能分隔線##

@login_required
def lessons_main_page(request):
    title = '開課! Quikok - 課程主頁'
    main_subjucts_list = ['國文','英文','數學']
    #if request.method == 'POST':
    #    subjects = request.POST.get('subjects')
    #    print(subjects)
    #if 'subjects' in request.POST:
    #    if request.POST['subjects'] is not '':
    #        print(request.POST['platform'])
    
    ## 08.26 建了許多老師假資料後回頭來串接這邊
    current_teacher = teacher_profile.objects.all()
    return render(request, 'lesson/lessons_main_page.html', locals())


@require_http_methods(['POST'])
def get_lesson_cards_for_common_users(request):
    # 20200911 暫時不開發排序、篩選部分
    # 接收：需要多少小卡(int)、排序依據(string)、篩選依據(string)、觀看的用戶
    # 20201103 加入篩選機制，未來再重構此一api
    def get_teacher_auth_ids_who_have_set_available_times():
            the_teacher_manager = teacher_manager()
            teacher_auth_ids_with_live_lessons = \
                the_teacher_manager.get_teacher_ids_who_have_lessons_on_sale()
            live_teacher_auth_ids_and_times_dict = \
                the_teacher_manager.get_teacher_s_available_time(teacher_auth_ids_with_live_lessons)
            matched_teacher_auth_ids = list()
            for key_auth_id, value_time in live_teacher_auth_ids_and_times_dict.items():
                # print('get_teacher_auth_ids_who_have_set_available_times',
                # key_auth_id, value_time, len(value_time))
                #if not len(value_time) == 0:
                    # 如果沒有空閒時間就可以直接跳過了
                    # 現在先不要這樣好了
                matched_teacher_auth_ids.append(key_auth_id)
            return matched_teacher_auth_ids

    qty = request.POST.get('qty', False) # 暫定六堂課
    filtered_by = request.POST.get('filtered_by', False)
    keywords = request.POST.get('keywords', False)
    ordered_by = request.POST.get('ordered_by', False)
    user_auth_id = request.POST.get('userID', False)
    only_show_ones_favorites = request.POST.get('only_show_ones_favorites', False)
    only_show_lessons_by_this_teacher_s_auth_id = \
        request.POST.get('only_show_lessons_by_this_teacher_s_auth_id', False)
    response = {}
    if not check_if_all_variables_are_true(qty, user_auth_id,
    keywords, filtered_by, ordered_by):
        # 之後等加入條件再改寫法 
        # 收取的資料不正確
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed'
        response['data'] = None
        return JsonResponse(response)
    else:
        # 收取的資料正確，準備撈資料回傳
        # order_by 跟 filtered_by 暫時不寫
        if int(qty) == -1:
            # 不指定顯示數量，全部都要回傳
            qty = None
        else:
            qty = int(qty)
        only_show_ones_favorites = only_show_ones_favorites == 'true'
        _data = []
        lesson_info_selling_objects = lesson_info.objects.filter(selling_status='selling')
        the_lesson_manager = lesson_manager()
        if_there_was_any_filtering = the_lesson_manager.parse_filtered_conditions(filtered_by)
        
        # 即使沒有設定空閒時間參數或篩選資訊，也只回傳有空閒時段的老師
        
        if if_there_was_any_filtering:
            # 代表user有輸入篩選資訊
            if the_lesson_manager.current_filtered_times is not None:
                # current_filtered_times >>
                # [1, 2, 3, 4, 5, 10, 22, 35, 44....]
                # 先看哪一些老師符合裡面的時段，然後列出這些老師所有的課程id即可
                #   step1: 先列出每一個老師的總和unique_time
                the_teacher_manager = teacher_manager()
                teacher_auth_ids_with_live_lessons = \
                    the_teacher_manager.get_teacher_ids_who_have_lessons_on_sale()
                live_teacher_auth_ids_and_times_dict = \
                    the_teacher_manager.get_teacher_s_available_time(teacher_auth_ids_with_live_lessons)
                matched_teacher_auth_ids = list()
                for key_auth_id, value_time in live_teacher_auth_ids_and_times_dict.items():
                    if len(value_time) > 0:
                        # 如果沒有空閒時間就可以直接跳過了
                        for each_teacher_s_time in value_time:
                            if each_teacher_s_time in the_lesson_manager.current_filtered_times:
                                # 老師的時間跟user篩選的時段重疊，這個老師的課程可以被顯示
                                matched_teacher_auth_ids.append(key_auth_id)
                                break
                # 已經取得了所有符合條件的老師，接著只要把這些老師的課程id回傳到下一個篩選機制就好了
                lesson_info_selling_objects = \
                    lesson_info_selling_objects.filter(teacher__auth_id__in = matched_teacher_auth_ids)     

            if the_lesson_manager.current_filtered_price_per_hour is not None:
                lesson_info_selling_objects = lesson_info_selling_objects.filter(price_per_hour__gt=the_lesson_manager.current_filtered_price_per_hour[0]-1).filter(price_per_hour__lt=the_lesson_manager.current_filtered_price_per_hour[1]+1)
                # 限制鐘點費需要介於(含)最高與最低之間
            if the_lesson_manager.current_filtered_subjects is not None:
                for i, each_subject in enumerate(the_lesson_manager.current_filtered_subjects):
                    if i == 0:
                        query = Q(lesson_attributes__contains=each_subject)
                    else:
                        query.add(Q(lesson_attributes__contains=each_subject), Q.OR)
                lesson_info_selling_objects = lesson_info_selling_objects.filter(query)
            if the_lesson_manager.current_filtered_target_students is not None:
                for i, each_target_student in enumerate(the_lesson_manager.current_filtered_target_students):
                    if i == 0:
                        query = Q(lesson_attributes__contains=each_target_student)
                    else:
                        query.add(Q(lesson_attributes__contains=each_target_student), Q.OR)
                lesson_info_selling_objects = lesson_info_selling_objects.filter(query)
            if the_lesson_manager.current_filtered_tutoring_experience is not None:
                for i, each_tutoring_experience in enumerate(the_lesson_manager.current_filtered_tutoring_experience):
                    if i == 0:
                        query = Q(tutor_experience=each_tutoring_experience)
                    else:
                        query.add(Q(tutor_experience=each_tutoring_experience), Q.OR)
                matched_teacher_ids = teacher_profile.objects.filter(query).values_list('id', flat=True)
                lesson_info_selling_objects = lesson_info_selling_objects.filter(teacher_id__in = matched_teacher_ids)
                
        selling_lessons_ids = lesson_info_selling_objects.values_list('id', flat=True)

        user_s_all_favorite_lessons_ids = \
            favorite_lessons.objects.filter(follower_auth_id = user_auth_id).values_list('lesson_id', flat=True)
        if int(only_show_lessons_by_this_teacher_s_auth_id) == -1:
            # 所有老師的課程小卡都show出來
            if only_show_ones_favorites:
                # 只show出用戶有收藏的上架中的課程小卡
                ones_favorite_and_selling_lessons_set = lesson_card.objects.filter(id__in=user_s_all_favorite_lessons_ids).filter(corresponding_lesson_id__in=selling_lessons_ids)[:qty].values()
                for each_lesson_card_object_values in ones_favorite_and_selling_lessons_set:
                    lesson_attributes = each_lesson_card_object_values
                    lesson_attributes['is_this_my_favorite_lesson'] = True
                    lesson_attributes.pop('id', None)
                    lesson_attributes['lessonID'] = lesson_attributes['corresponding_lesson_id']
                    lesson_attributes.pop('corresponding_lesson_id', None)
                    # 以上drop掉這兩個keys
                    _data.append(lesson_attributes)
            else:
                # show出所有上架中的課程小卡
                lesson_card_objects_values_set = lesson_card.objects.filter(corresponding_lesson_id__in = selling_lessons_ids)[:qty].values()
                for each_lesson_card_object_values in lesson_card_objects_values_set:
                    lesson_attributes = each_lesson_card_object_values
                    lesson_attributes['is_this_my_favorite_lesson'] = \
                        lesson_attributes['corresponding_lesson_id'] in user_s_all_favorite_lessons_ids
                    lesson_attributes.pop('id', None)
                    lesson_attributes['lessonID'] = lesson_attributes['corresponding_lesson_id']
                    lesson_attributes.pop('corresponding_lesson_id', None)
                    # 以上drop掉這兩個keys  
                    _data.append(lesson_attributes)
        else:
            # 只show出指定老師的上架中的課程小卡
            that_teacher_auth_id = int(only_show_lessons_by_this_teacher_s_auth_id)
            if only_show_ones_favorites:
                # 只show出用戶有收藏的指定老師的上架中的課程小卡
                ones_favorite_and_selling_lessons_set = lesson_card.objects.filter(teacher_auth_id=that_teacher_auth_id).filter(id__in=user_s_all_favorite_lessons_ids).filter(corresponding_lesson_id__in=selling_lessons_ids)[:qty].values()   
                for each_lesson_card_object_values in ones_favorite_and_selling_lessons_set:
                    lesson_attributes = each_lesson_card_object_values
                    lesson_attributes['is_this_my_favorite_lesson'] = True
                    lesson_attributes.pop('id', None)
                    lesson_attributes['lessonID'] = lesson_attributes['corresponding_lesson_id']
                    lesson_attributes.pop('corresponding_lesson_id', None)
                    # 以上drop掉這兩個keys
                    _data.append(lesson_attributes)
            else:
                # show出所有上架中的指定老師的課程小卡
                lesson_card_objects_values_set = lesson_card.objects.filter(teacher_auth_id=that_teacher_auth_id).filter(corresponding_lesson_id__in = selling_lessons_ids)[:qty].values()
                user_s_all_favorite_lessons_ids = \
                    favorite_lessons.objects.filter(follower_auth_id = user_auth_id).values_list('lesson_id', flat=True)
                
                for each_lesson_card_object_values in lesson_card_objects_values_set:
                    lesson_attributes = each_lesson_card_object_values
                    lesson_attributes['is_this_my_favorite_lesson'] = \
                        lesson_attributes['corresponding_lesson_id'] in user_s_all_favorite_lessons_ids
                    lesson_attributes.pop('id', None)
                    lesson_attributes['lessonID'] = lesson_attributes['corresponding_lesson_id']
                    lesson_attributes.pop('corresponding_lesson_id', None)
                    # 以上drop掉這兩個keys  
                    _data.append(lesson_attributes)
        

        # 刪掉沒有「設定空閒時間的老師」的課程
        lesson_ids_with_teacher_setting_available_times = \
            lesson_info.objects.filter(
                teacher__auth_id__in = \
                    get_teacher_auth_ids_who_have_set_available_times()
                ).values_list('id', flat=True)
        #print('lesson_ids_with_teacher_setting_available_times',
        lesson_ids_with_teacher_setting_available_times,
        #len(lesson_ids_with_teacher_setting_available_times))

        if len(lesson_ids_with_teacher_setting_available_times) == 0:
            # 萬一沒有老師有空，自然就不用show課程了
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = list()
            return JsonResponse(response)
        else:
            _data = \
                list(filter(
                    lambda x: x['lessonID'] in lesson_ids_with_teacher_setting_available_times,
                    _data))
        
        if len(keywords) > 0:
            seaman = sea_man()
            #the_lesson_info = lesson_info()
            '''['teacher__nickname', 'teacher__name', 'intro', 'subject_type',
                    'education_1', 'education_2', 'education_3', 'company', 'special_exp',
                    'big_title', 'little_title', 'lesson_title', 'highlight_1', 'highlight_2', 'highlight_3',
                    'how_does_lesson_go', 'target_students', 'lesson_remarks', 'syllabus',
                    'lesson_attributes']'''
            matched_lesson_ids = \
                seaman.get_model_key_value_where_a_is_in_its_specific_columns(
                    keywords, 
                    ['big_title', 'little_title', 'lesson_title', 'highlight_1', 'highlight_2', 'highlight_3',
                    'how_does_lesson_go', 'target_students', 'lesson_remarks', 'syllabus', 'lesson_attributes'],
                    'id',
                    lesson_info_selling_objects
                )
            for each_dict in _data:
                if each_dict['lessonID'] not in matched_lesson_ids:
                    _data.remove(each_dict)
            #print(len(_data))
        if len(ordered_by) > 0:
            the_lesson_card_manager = lesson_card_manager()
            sorted_lesson_ids = the_lesson_card_manager.sort_lessons_id_by(
                [_['lessonID'] for _ in _data],
                ordered_by)
            _data = sort_dictionaries_in_a_list_by_specific_key(
                'lessonID', 
                sorted_lesson_ids,
                _data)
        
        response['status'] = 'success'
        response['errCode'] = None
        response['errMsg'] = None
        response['data'] = _data
        return JsonResponse(response)


@require_http_methods(['GET'])
def get_lesson_cards_for_the_teacher_who_created_them(request):
    user_auth_id = request.GET.get('userID', False)
    # 這裡的user_auth_id就是指那個老師
    response = {}
    if not user_auth_id:
        # 之後等加入條件再改寫法 
        # 收取的資料不正確
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Found no teacher.'
        response['data'] = None
        return JsonResponse(response)
    else:
        # 收取的資料正確，準備撈資料回傳
        # order_by 跟 filtered_by 暫時不寫
        data = []
        lesson_objects = lesson_info.objects.filter(teacher__auth_id = user_auth_id)

        def intro_briefed(intro_texts, length=32):
            _ = intro_texts[:length].strip()
            if len(_) == 32:
                return _ + '...'
            else:
                return _

        for each_lesson_object in lesson_objects:
            lesson_attributes = {}
            lesson_attributes['lesson_id'] = each_lesson_object.id
            lesson_attributes['lesson_status'] = each_lesson_object.selling_status
            lesson_attributes['price_per_hour'] = each_lesson_object.price_per_hour
            lesson_attributes['brief_lesson_intro'] = intro_briefed(each_lesson_object.lesson_intro)
            lesson_attributes['background_picture_code'] = each_lesson_object.background_picture_code
            lesson_attributes['background_picture_path'] = each_lesson_object.background_picture_path
            lesson_attributes['lesson_title'] = each_lesson_object.lesson_title

            sales_package = list()
            if each_lesson_object.trial_class_price != -999 :
                sales_package.append('試教 $' + str(each_lesson_object.trial_class_price))
            if each_lesson_object.lesson_has_one_hour_package:
                sales_package.append('單堂販售')
            for i, j in [_.split(':') for _ in each_lesson_object.discount_price.split(';') if len(_)]:
                sales_package.append(i + '小時 ' + j + '%')
            lesson_attributes['sales_package'] = sales_package   # ';'.join(sales_package)

            data.append(lesson_attributes)
        
        response['status'] = 'success'
        response['errCode'] = None
        response['errMsg'] = None
        response['data'] = data
        return JsonResponse(response)


@require_http_methods(['POST'])
def add_or_remove_favorite_lessons(request):
    user_auth_id = request.POST.get('userID', False)
    lesson_id = request.POST.get('lessonID', False)
    response = {}
    if not check_if_all_variables_are_true(user_auth_id, lesson_id):
        # 之後等加入條件再改寫法 
        # 收取的資料不正確
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed'
        return JsonResponse(response)
    if int(user_auth_id) == -1:
        response['status'] = 'failed'
        response['errCode'] = '1'
        response['errMsg'] = 'User Is Anonymous.'
        return JsonResponse(response)
    favorite_lessons_object = favorite_lessons.objects.filter(follower_auth_id=user_auth_id).filter(lesson_id=lesson_id).first()
    if favorite_lessons_object is None:
        # 代表這門課還不是該user的喜好，我們要加進去
        favorite_lessons.objects.create(
            follower_auth_id = user_auth_id,
            lesson_id = lesson_id,
            teacher_auth_id = teacher_profile.objects.filter(id=lesson_info.objects.filter(id=lesson_id).first().teacher_id).first().auth_id
        ).save()
    else:
        # 代表這門課已經是該user的喜好，我們要移除
        favorite_lessons_object.delete()
    response['status'] = 'success'
    response['errCode'] = None
    response['errMsg'] = None
    return JsonResponse(response)

@require_http_methods(['GET'])
def get_all_filtered_keys_and_values(request):
    response = dict()
    data = dict()
    the_lesson_manager = lesson_manager()
    filtered_subjects = the_lesson_manager.filtered_subjects
    filtered_target_students = the_lesson_manager.filtered_target_students
    filtered_times = the_lesson_manager.filtered_times
    filtered_tutoring_experience = the_lesson_manager.filtered_tutoring_experience
    mapping_index = {
        0: 'filtered_subjects',
        1: 'filtered_target_students',
        2: 'filtered_times',
        3: 'filtered_tutoring_experience'
    }
    for i, each_filtering in enumerate([filtered_subjects, filtered_target_students,
    filtered_times, filtered_tutoring_experience]):
        # 'filtered_subjects': [
        #   {text:國文, value:0, select:False},
        #   {text:英文, value:1, select:False},
        # ...]
        _data_dict_content = list()
        for key, value in each_filtering.items():
            _data_dict_content.append(
                {
                    'text': value,
                    'value': key,
                    'select': False,
                }
            )
        data[mapping_index[i]] = _data_dict_content
    response['status'] = 'success'
    response['errCode'] = None
    response['errMsg'] = None
    response['data'] = data
    return JsonResponse(response)


def import_lesson(request):
    title = '批次匯入課程'
    folder_where_are_uploaded_files_be = 'temp' # 
    if request.method == 'POST':
        fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
        for each_file in request.FILES.getlist("files"):
            fs.save(each_file.name, each_file)
            if each_file.name.endswith(('xlsx', 'xls')):
                df_lesson = pd.read_excel(os.path.join(folder_where_are_uploaded_files_be, each_file.name))
                for each_row_num in range(df_lesson.shape[0]):
                    #print(each_row)
                    teacher_id = teacher_profile.objects.get(id = each_row_num+1) #ForeignKey
                    lesson_info.objects.create(
                    lesson_id = df_lesson['lesson_id'][each_row_num],
                    big_title = df_lesson['big_title'][each_row_num],
                    little_title = df_lesson['little_title'][each_row_num],
                    teacher = teacher_id,
                    lesson_title = df_lesson['lesson_title'][each_row_num],
                    price_per_hour = df_lesson['price_per_hour'][each_row_num],
                    highlight_1 = df_lesson['highlight_1'][each_row_num],
                    highlight_2 = df_lesson['highlight_2'][each_row_num],
                    highlight_3 = df_lesson['highlight_3'][each_row_num],
                    lesson_intro = df_lesson['lesson_intro'][each_row_num],
                    how_does_lesson_go = df_lesson['how_does_lesson_go'][each_row_num],
                    target_students = df_lesson['target_students'][each_row_num],
                    lesson_remarks = df_lesson['lesson_remarks'][each_row_num],
                    lesson_background_folder = df_lesson['lesson_background_folder'][each_row_num],
                    lesson_picture_folder = '',
                    syllabus = df_lesson['syllabus'][each_row_num],
                    lesson_appendix_folder ='',
                    lesson_attributes =df_lesson['lesson_attributes'][each_row_num],
                    lesson_avg_score = 0,
                    lesson_reviewed_times = 0,
                    ).save()
                    print('成功匯入課程:'+ df_lesson['lesson_title'][each_row_num])
            else:
                print('我只收xlsx,xls檔')        
        os.unlink(os.path.join(folder_where_are_uploaded_files_be, each_file.name))
    return render(request, 'lesson/import_lesson.html',locals())


@require_http_methods(['GET'])
def return_lesson_details_for_teacher_who_created_it(request):
    # http://127.0.0.1:8000/api/lesson/returnLessonDetailsForTeacherWhoCreatedIt/?action=editLesson&userID=2&lessonID=1
    response = dict()
    action = request.GET.get('action', False)
    teacher_auth_id = request.GET.get('userID', False)
    lesson_id = request.GET.get('lessonID', False)
    the_lesson_manager = lesson_manager()
    #print('action', action)
    #print('teacher_auth_id', teacher_auth_id)
    #print('lesson_id', lesson_id)

    if action != 'editLesson':
        response['status'] = 'failed'
        response['errCode'] = 0
        response['errMsg'] = 'Unknown Action'
        response['data'] = None
        return JsonResponse(response)
    else:
        # print('check1')
        try:   
            status, errCode, errMsg, _data = the_lesson_manager.return_lesson_details(
                lesson_id=lesson_id,
                user_auth_id = teacher_auth_id,
                for_whom='teacher_who_created_it',
            )
           
            response['status'] = status
            response['errCode'] = errCode
            response['errMsg'] = errMsg
            response['data'] = _data
            return JsonResponse(response)
        except:
            response['status'] = 'failed'
            response['errCode'] = 3
            response['errMsg'] = 'Querying Failed.'
            response['data'] = None
            return JsonResponse(response)
            

@require_http_methods(['GET'])
def return_lesson_details_for_browsing(request):
    response = dict()
    the_lesson_manager = lesson_manager()
    action = request.GET.get('action', False)
    teacher_auth_id = request.GET.get('userID', False)
    lesson_id = request.GET.get('lessonID', False)

    if action != 'browsing':
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Unknown Action'
        response['data'] = None
        return JsonResponse(response)
    else:
        try:
            status, errCode, errMsg, _data = the_lesson_manager.return_lesson_details(
                lesson_id=int(lesson_id),
                user_auth_id = teacher_auth_id,
                for_whom='common_users',
            )
            response['status'] = status
            response['errCode'] = errCode
            response['errMsg'] = errMsg
            response['data'] = _data
            return JsonResponse(response)
        except:
            response['status'] = 'failed'
            response['errCode'] = '3'
            response['errMsg'] = 'Querying Failed.'
            response['data'] = None
            return JsonResponse(response)


@require_http_methods(['POST'])
def create_or_edit_a_lesson(request):

    response = dict()
    action = request.POST.get('action', False)
    teacher_auth_id = request.POST.get('userID', False)
    lesson_id = request.POST.get('lessonID', False)  # 新增沒有, 修改才有
    the_leeson_manager = lesson_manager()

    if not check_if_all_variables_are_true(action, teacher_auth_id):
        # 萬一有變數沒有傳到後端來的話...
        response['status'] = 'failed'
        response['errCode'] = 0
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        return JsonResponse(response)

    if action == 'createLesson':
        # 課程新增
        response['status'], response['errCode'], response['errMsg'], response['data']= \
            the_leeson_manager.setup_a_lesson(
                teacher_auth_id, request, None, action)

        object_accessed_signal.send(
            sender='create_or_edit_a_lesson',
            auth_id=teacher_auth_id,
            ip_address=get_client_ip(request),
            url_path=request.META.get('PATH_INFO'),
            model_name='lesson_info',
            object_name=request.POST.get('lesson_title'),
            object_id=response.get('data'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            action_type='create lesson after signup',
            remark=None) # 傳送訊號

        if response['status'] == 'success':
            try:
                # 確定成功再來更新 sales_sets
                # 先把一些共同的欄位合併在一個list內
                the_lesson_info_object = lesson_info.objects.filter(id=response['data']).first()
                shared_columns = {
                    'lesson_id': response['data'],
                    'teacher_auth_id': the_lesson_info_object.teacher.auth_id,
                    'price_per_hour': the_lesson_info_object.price_per_hour 
                }
                
                if the_lesson_info_object.selling_status == 'selling':
                    # 假設是 status: selling 再來進行，反之則不必
                    # 即使非 selling ，也不需要 inactivate old sales_sets ，因為是新建立的課程

                    # 要先確定 1.是否有試課方案  2.是否有單堂方案  3.其他方案(\d*:\d*的格式) 
                    if the_lesson_info_object.trial_class_price != -999:
                        # 有試課方案
                        shared_columns['sales_set'] = 'trial'
                        shared_columns['total_hours_of_the_sales_set'] = 1
                        shared_columns['price_per_hour_after_discount'] = the_lesson_info_object.trial_class_price
                        shared_columns['total_amount_of_the_sales_set'] = the_lesson_info_object.trial_class_price
                        
                        lesson_sales_sets.objects.create(
                            **shared_columns
                        ).save()
                    
                    if the_lesson_info_object.lesson_has_one_hour_package == True:
                        # 有單堂方案
                        shared_columns['sales_set'] = 'no_discount'
                        shared_columns['total_hours_of_the_sales_set'] = 1
                        shared_columns['price_per_hour_after_discount'] = the_lesson_info_object.price_per_hour
                        shared_columns['total_amount_of_the_sales_set'] = the_lesson_info_object.price_per_hour

                        lesson_sales_sets.objects.create(
                            **shared_columns
                        ).save()

                    if len(the_lesson_info_object.discount_price) > 2:
                        # 有其他方案
                        for each_hours_discount_set in [_ for _ in the_lesson_info_object.discount_price.split(';') if len(_) > 0]:
                            
                            hours, discount_price = each_hours_discount_set.split(':')
                            shared_columns['sales_set'] = each_hours_discount_set
                            shared_columns['total_hours_of_the_sales_set'] = int(hours)
                            shared_columns['price_per_hour_after_discount'] = round(the_lesson_info_object.price_per_hour * int(discount_price) / 100)
                            shared_columns['total_amount_of_the_sales_set'] = round(the_lesson_info_object.price_per_hour * int(hours) * int(discount_price) / 100)

                            lesson_sales_sets.objects.create(
                                **shared_columns
                            ).save()
            except Exception as e:
                print(f'Exception: {e}')
                response['status'] = 'failed'
                response['errCode'] = '5'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                response['data'] = None

        return JsonResponse(response)

    elif action == 'editLesson':

        if not lesson_id:
            # 沒有傳入要編輯的 lesson_id
            response['status'] = 'failed'
            response['errCode'] = '6'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
        
        else:

            response['status'], response['errCode'], response['errMsg'], response['data']= \
                the_leeson_manager.setup_a_lesson(
                    teacher_auth_id, request, lesson_id, action)

            if response['status'] == 'success':
                # 確定成功再來更新 sales_sets
                try:    
                    # 先把一些共同的欄位合併在一個list內
                    the_lesson_info_object = lesson_info.objects.filter(id=response['data']).first()
                    shared_columns = {
                        'lesson_id': response['data'],
                        'teacher_auth_id': the_lesson_info_object.teacher.auth_id,
                        'price_per_hour': the_lesson_info_object.price_per_hour 
                    }
                    # 要先將舊版的 sales_sets 狀態設成 closed >> is_open: False
                    # 但如果只是修改 selling_status 呢? >>
                    #   這樣好了，只有當 selling_status 為 "selling" 時才紀錄 lesson_sales_sets，
                    #   其他時候只要把存在的 sales_sets 改為 is_open: False 就好了
                    if the_lesson_info_object.selling_status == 'selling':
                        
                        # 先將舊的 sales_sets inactivate
                        for each_sales_set in lesson_sales_sets.objects.filter(lesson_id=response['data']).filter(is_open=True):
                            setattr(each_sales_set, 'is_open', False)
                            each_sales_set.save()

                        # 要確定 1.是否有試課方案  2.是否有單堂方案  3.其他方案(\d*:\d*的格式)
                        if the_lesson_info_object.trial_class_price != -999:
                            # 有試課方案
                            shared_columns['sales_set'] = 'trial'
                            shared_columns['total_hours_of_the_sales_set'] = 1
                            shared_columns['price_per_hour_after_discount'] = the_lesson_info_object.trial_class_price
                            shared_columns['total_amount_of_the_sales_set'] = the_lesson_info_object.trial_class_price
                            
                            lesson_sales_sets.objects.create(
                                **shared_columns
                            ).save()
                        
                        if the_lesson_info_object.lesson_has_one_hour_package == True:
                            # 有單堂方案
                            shared_columns['sales_set'] = 'no_discount'
                            shared_columns['total_hours_of_the_sales_set'] = 1
                            shared_columns['price_per_hour_after_discount'] = the_lesson_info_object.price_per_hour
                            shared_columns['total_amount_of_the_sales_set'] = the_lesson_info_object.price_per_hour

                            lesson_sales_sets.objects.create(
                                **shared_columns
                            ).save()

                        if len(the_lesson_info_object.discount_price) > 2:
                            # 有其他方案
                            for each_hours_discount_set in [_ for _ in the_lesson_info_object.discount_price.split(';') if len(_) > 0]:
                                
                                hours, discount_price = each_hours_discount_set.split(':')
                                shared_columns['sales_set'] = each_hours_discount_set
                                shared_columns['total_hours_of_the_sales_set'] = int(hours)
                                shared_columns['price_per_hour_after_discount'] = round(the_lesson_info_object.price_per_hour * int(discount_price) / 100)
                                shared_columns['total_amount_of_the_sales_set'] = round(the_lesson_info_object.price_per_hour * int(hours) * int(discount_price) / 100)

                                lesson_sales_sets.objects.create(
                                    **shared_columns
                                ).save()
                    else:
                        # 因為最新的課程狀態不是 selling ，因此把 sales_sets 取消 active 就好了
                        for each_sales_set in lesson_sales_sets.objects.filter(lesson_id=response['data']).filter(is_open=True):
                            setattr(each_sales_set, 'is_open', False)
                            each_sales_set.save()
                                
                except Exception as e:
                    print(f'Exception: {e}')
                    response['status'] = 'failed'
                    response['errCode'] = '5'
                    response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                    response['data'] = None  
                
        return JsonResponse(response)

    else:
        response['status'] = 'failed'
        response['errCode'] = 1
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
        return JsonResponse(response)


@require_http_methods(['POST'])
def set_lesson_s_status(request):
    response = dict()
    action = request.POST.get('selling_status', False)
    teacher_auth_id = request.POST.get('userID', False)
    lesson_id = request.POST.get('lessonID', False) 
    #print(action, teacher_auth_id, lesson_id)

    if not check_if_all_variables_are_true(action, teacher_auth_id, lesson_id):
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        return JsonResponse(response)
    
    vaildated_lesson_object = \
        lesson_info.objects.filter(teacher__auth_id=teacher_auth_id).filter(id=lesson_id).first()
    if vaildated_lesson_object is None:
        response['status'] = 'failed'
        response['errCode'] = '1'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        return JsonResponse(response)
    else:
        # 有找到對應的課程
        if action in ['selling', 'notSelling', 'donotShow']:
            setattr(vaildated_lesson_object, 'selling_status', action)
            vaildated_lesson_object.save()
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            return JsonResponse(response)
        else:
            response['status'] = 'failed'
            response['errCode'] = '2'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            return JsonResponse(response)

    
def fake_form(request):
    if request.method == 'POST':
        v = request.POST.get("t_input", False)
        print('v >>  ', v)
        print('is v False >>  ', v == False)
        print('is v None >>  ', v is None)
        print('is v an empty string >>  ', v == '')
        print('if v is not false, it might print a "COOL"...')
        if v:
            print("COOL")
        print('End of line.')
        return HttpResponse("GOT IT.")
    else:
        return render(request, 'lesson/fake_form.html')




def lesson_manage(request):
    # 新增課程
    response = {}
    the_lesson_card_manager = lesson_card_manager()
    # 創建lesson_card_manager類別

    # 當學生瀏覽課程、老師預覽/修改上架內容
    # 差異化的功能selling_status<學生瀏覽課程調資料時應該不用回傳@@ 或是只回傳selling?
    if request.method == 'GET' :
        #action = request.POST.get('action', False)#測試用
        action = request.GET.get('action', False)
        if action == 'showLesson':
            # 取得課程內容
            # lesson_id = request.POST.get('lessonID', False) 
            lesson_id = request.GET.get('lesson_id', False) # 測試用
            # lesson_id是False也會回傳none
            lesson_object = lesson_info.objects.filter(id = lesson_id).first()
            if lesson_object is None:
                response['status'] = 'failed'
                response['errCode'] = '0'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            else:
                big_title = lesson_object.big_title
                little_title = lesson_object.little_title
                title_color = lesson_object.title_color
                background_picture_code = lesson_object.background_picture_code
                background_picture_path = lesson_object.background_picture_path
                lesson_title = lesson_object.lesson_title
                price_per_hour= lesson_object.price_per_hour
                trial_class_price = lesson_object.trial_class_price
                discount_price = lesson_object.discount_price
                highlight_1 = lesson_object.highlight_1
                highlight_2 = lesson_object.highlight_2
                highlight_3 = lesson_object.highlight_3
                lesson_intro = lesson_object.lesson_intro 
                how_does_lesson_go = lesson_object.how_does_lesson_go
                target_students = lesson_object.target_students
                syllabus = lesson_object.syllabus
                lesson_remarks = lesson_object.lesson_remarks
                lesson_attributes = lesson_object.lesson_attributes
                selling_status = lesson_object.selling_status
            
                if  [lesson_title, price_per_hour, lesson_intro, selling_status]:
                    data = [{
                        'big_title' : big_title,
                        'little_title' :little_title,
                        'title_color' : title_color,
                        'default_background_picture' : background_picture_code,
                        'background_picture' : background_picture_path,
                        'lesson_title' : lesson_title,
                        'price_per_hour' :price_per_hour,
                        'trial_class_price': trial_class_price,
                        'discount_price' :discount_price,
                        'highlight_1':highlight_1,
                        'highlight_2':highlight_2,
                        'highlight_3': highlight_3,
                        'lesson_intro': lesson_intro,
                        'how_does_lesson_go': how_does_lesson_go,
                        'target_students':target_students,
                        'syllabus':syllabus,
                        'lesson_remarks':lesson_remarks,
                        'lesson_attributes':lesson_attributes,
                        'selling_status': selling_status
                    }]
                    response = {
                    'status': 'success',
                    'errCode': None,
                    'errMsg': None,
                    'data' :data
                    }
                    #print(response)
                else:
                    response['status'] = 'failed'
                    response['errCode'] = '1'
                    response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            return JsonResponse(response) 
            #return render(request, 'lesson/create_lesson.html') #測試頁面

    if request.method == 'POST':
        action = request.POST.get('action', False) # 新增或修改課程
        lesson_id = request.POST.get('lessonID', False) # 新增沒有,修改才有
        # 修改應該只比新增多 "課程id" 這個資訊要拿
        #auth_id = request.POST.get('userID', False)
        auth_id = 2 # 測試用
        teacher_username = User.objects.get(id = auth_id).username
        # 用老師username當key從auth找profile
        teacher = teacher_profile.objects.get(username = teacher_username)
        
        big_title = request.POST.get('big_title', False)
        little_title= request.POST.get('little_title', False)
        title_color= request.POST.get('title_color', False)
        background_picture_code= request.POST.get('choose_background_picture', False)
        lesson_title = request.POST.get('lesson_title', False)
        
        price_per_hour= request.POST.get('price_per_hour', False)
        #price_per_hour = 300
        unit_class_price = request.POST.get('unitClassPrice', False)
        if unit_class_price:
            lesson_has_one_hour_package = True
        else:
            lesson_has_one_hour_package = False
        #unit_class_price = 300
        #單節費用 有勾選前端回傳鐘點費金額 無勾選前端回傳null
        trial_class_price = request.POST.get('trialClassPrice', 0)
        discount_price = request.POST.get('discountPrice', 0)
        highlight_1 = request.POST.get('highlight_1', False) 
        highlight_2 = request.POST.get('highlight_2', False)
        highlight_3 = request.POST.get('highlight_3', False)
        lesson_intro = request.POST.get('lesson_intro', False)
        how_does_lesson_go = request.POST.get('how_does_lesson_go', False)
        target_students = request.POST.get('target_students', False)
        syllabus = request.POST.get('syllabus', False)
        lesson_remarks = request.POST.get('lesson_remarks', False)
        lesson_attributes = request.POST.get('lesson_attributes', False)
        selling_status = request.POST.get('sellStatus', False)

        if action == 'editLesson': 
            # 如果 lesson_id 有值表示是要修改欄位,多加一個action條件防意外
            if  [lesson_id, teacher, lesson_title, price_per_hour, lesson_intro]:
                lesson_obj = lesson_info.objects.filter(id = lesson_id)
                if lesson_obj:
                    lesson_obj.update(
                        big_title = big_title,
                        little_title= little_title,
                        title_color = title_color,
                        background_picture_code= background_picture_code,
                        background_picture_path = background_picture_path,
                        lesson_title = lesson_title,
                        price_per_hour= price_per_hour,
                        lesson_has_one_hour_package = lesson_has_one_hour_package,
                        trial_class_price = trial_class_price,
                        discount_price = discount_price,
                        highlight_1 = highlight_1,
                        highlight_2 = highlight_2,
                        highlight_3 = highlight_3,
                        lesson_intro = lesson_intro,
                        how_does_lesson_go = how_does_lesson_go,
                        target_students = target_students,
                        syllabus = syllabus,
                        lesson_remarks = lesson_remarks,
                        lesson_attributes=  lesson_attributes,
                        selling_status = selling_status
                    )

                    # ================課程小卡================
                    the_lesson_card_manager.setup_a_lesson_card(
                        corresponding_lesson_id = lesson_id,
                        teacher_auth_id = auth_id,
                    )
                    # ================課程小卡================ 

                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                else:
                    response['status'] = 'failed'
                    response['errCode'] = 0
                    response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            
            else:            # 資料傳輸有問題
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'



        # 新增lesson 時的必填欄位, 不得為 False, 雖然前端有做處理但這邊再防傳輸問題
        elif  action == 'createLesson':
            if [selling_status, teacher, lesson_title, price_per_hour, lesson_intro]:
                
                new_created_object = \
                    lesson_info.objects.create(
                        #lesson_id = lesson_id, 
                        #teacher =teacher 
                        teacher = teacher, #測試
                        big_title = big_title,
                        little_title= little_title,
                        title_color = title_color,
                        #default_background_picture= default_background_picture,
                        background_picture_code= background_picture_code,
                        background_picture_path = '', # 這個值在此課程的資料夾建立後再update填入
                        lesson_title = lesson_title,
                        price_per_hour= price_per_hour,
                        lesson_has_one_hour_package = lesson_has_one_hour_package,
                        trial_class_price = trial_class_price,
                        discount_price = discount_price,
                        highlight_1 = highlight_1,
                        highlight_2 = highlight_2,
                        highlight_3 = highlight_3,
                        lesson_intro = lesson_intro,
                        how_does_lesson_go = how_does_lesson_go,
                        target_students = target_students,
                        syllabus = syllabus,
                        lesson_remarks = lesson_remarks,
                        lesson_attributes=  lesson_attributes,
                        selling_status = selling_status
                        )
                new_created_object.save()

                # 創立這個課的資料夾
                # 為了要以該課程的id建立資料夾,需要query剛建立好的課程 id
                # 理論上老師剛新建的課程id會是最新(id最大)的
                #teacher_id = teacher_profile.objects.get(username = teacher_username)
                #latest_lesson_id = lesson_info.objects.filter(teacher_id = teacher.id).order_by('-id')[0]
                #latest_lesson_id = str(latest_lesson_id.id) # int轉str 檔名要用str
                lesson_id = str(new_created_object.id) # 這樣拿更快
                lesson_folder = os.path.join('user_upload/teachers/'+teacher_username +\
                    '/lessons/' +'lessonID_'+ lesson_id)
                # 建立課程資料夾
                if not os.path.isdir(lesson_folder):
                    os.mkdir(os.path.join(lesson_folder))
                # 儲存這個課的userupload_pic 自定義背景
                background = request.FILES.get("tUploadBackPic", False)
                if background is not False:
                    #print('課程自訂背景圖: ', background.name)
                    file_exten = background.name.split('.')[-1]
                    # 完整檔名
                    back_pic_full_name = 'lesson_'+ lesson_id +'_upload_back_pic'+'.'+ file_exten
                    # 完整路徑名稱
                    background_pic_path = 'user_upload/teachers/' + \
                    teacher_username + '/lessons/lessonID_' + lesson_id
                    fs = FileSystemStorage(location=background_pic_path)
                    fs.save(back_pic_full_name , background) # 改檔名
                    back_pic_path_add_name = background_pic_path +back_pic_full_name
                    # 寫入背景圖路徑
                    lesson_info.objects.filter(id = int(lesson_id)).update(background_picture_path = back_pic_path_add_name)
                else:
                    pass # 不更新背景景圖路徑    

                # ================課程小卡================
                the_lesson_card_manager.setup_a_lesson_card(
                        corresponding_lesson_id = new_created_object.id,
                        teacher_auth_id = auth_id,
                    )
                # ================課程小卡================ 
                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
            else:
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        else:
            # action不等於任何值
            response['status'] = 'failed'
            response['errCode'] = '2'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
    #print(response)
    return JsonResponse(response)    


@require_http_methods(['POST'])
def before_signing_up_create_or_edit_a_lesson(request):
    response = dict()

    dummy_teacher_id = request.POST.get('dummy_teacher_id', False)

    if dummy_teacher_id == False:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Non dummy_user_id'
        response['data'] = None
    else:
        background_picture_code = int(request.POST.get('background_picture_code', False))
        
        if background_picture_code != 99:
            # 用戶使用預設的背景圖
            background_picture_path = ''
        else:
            temp_folder = f'user_upload/temp/before_signed_up/{dummy_teacher_id}'
            uploaded_background_picture = request.FILES['background_picture_path']
            # 用戶自己上傳了背景圖
            if not os.path.isdir(temp_folder):
                os.mkdir(temp_folder)
            else:
                shutil.rmtree(temp_folder)
                os.mkdir(temp_folder)

            fs = FileSystemStorage(location=temp_folder)
            file_extension = uploaded_background_picture.name.split('.')[-1]
            fs.save('customized_lesson_background'+'.'+ file_extension , uploaded_background_picture)
            background_picture_path = '/' + temp_folder + '/' + 'customized_lesson_background.' + file_extension

        arguments_dict = {
            'dummy_teacher_id': dummy_teacher_id,
            'big_title': request.POST.get('big_title', False),
            'little_title': request.POST.get('little_title', False),
            'title_color': request.POST.get('title_color', False),
            'background_picture_code': background_picture_code,
            'background_picture_path': background_picture_path,
            'lesson_title': request.POST.get('lesson_title', False),
            'price_per_hour': request.POST.get('price_per_hour', False),
            'lesson_has_one_hour_package': request.POST.get('lesson_has_one_hour_package', False) == 'true',
            'trial_class_price': request.POST.get('trial_class_price', False),
            'highlight_1': request.POST.get('highlight_1', False),
            'highlight_2': request.POST.get('highlight_2', False),
            'highlight_3': request.POST.get('highlight_3', False),
            'lesson_intro': request.POST.get('lesson_intro', False),
            'how_does_lesson_go': request.POST.get('how_does_lesson_go', False),
            'target_students': request.POST.get('target_students', False),
            'lesson_remarks': request.POST.get('lesson_remarks', False),
            'syllabus': request.POST.get('syllabus', False),
            'lesson_attributes': request.POST.get('lesson_attributes', False)        
            }

        try:
            temp_lesson_info = lesson_info_for_users_not_signed_up.objects.create(
                **arguments_dict
            )
            temp_lesson_info.save()

            object_accessed_signal.send(
            sender='before_signing_up_create_or_edit_a_lesson',
            auth_id=None,
            ip_address=get_client_ip(request),
            url_path=request.META.get('PATH_INFO'),
            model_name='lesson_info_for_users_not_signed_up',
            object_name=dummy_teacher_id,
            object_id=temp_lesson_info.id,
            user_agent=request.META.get('HTTP_USER_AGENT'),
            action_type='create lesson before signup',
            remark=None) # 傳送訊號

            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = temp_lesson_info.id
        except:
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
    
    return JsonResponse(response)


@require_http_methods(['POST'])
def get_lesson_specific_available_time(request):

    '''
    回傳該門課程的老師可預約時段，以及已經被預約走了的時段。
    status: success / failed
    errCode: None
    errMsg: None
    data:[
        {
            availableTime://可預約時段,格式：[2020-10-27:2,5;2020-11-03:2;2020-11-10:2...]
            bookedTime://已預約,格式：[2020-11-03:2]
        }
    ]
    20210107 >> 加進 距今的兩個小時不顯示 「可預約 & 已預約」，避免學生誤點
    '''
    response = dict()
    student_auth_id = request.POST.get('userID', False)
    lesson_id = request.POST.get('lessonID', False)

    if not check_if_all_variables_are_true(student_auth_id, lesson_id):
        # 資料傳輸錯誤
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    else:
        # the_student_object = student_profile.objects.filter(auth_id=student_auth_id).first()
        # 無須檢查用戶是否存在，畢竟只是看可預約時段而已。
        #if the_student_object is None:
        #    # 該名使用者不存在
        #    response['status'] = 'failed'
        #    response['errCode'] = '1'
        #    response['errMsg'] = '不好意思，您需要登入並且'
        #    response['data'] = None
        the_lesson_info_object = lesson_info.objects.filter(id=lesson_id).first()
        
        if the_lesson_info_object is None:
            # 該門課程不存在
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
        
        else:
            #corresponding_teacher_auth_id = the_lesson_info_object.teacher__auth_id

            available_times = list()
            specific_available_time_objects = \
                specific_available_time.objects.filter(
                    teacher_model=the_lesson_info_object.teacher,
                    date__gte=date_function.today()).filter(is_occupied=False)
                # show出 >= 今日日期的資料

            for each_specific_available_time_object in specific_available_time_objects:
                the_date = str(each_specific_available_time_object.date)
                available_times.append(
                    f'{the_date}:{each_specific_available_time_object.time};'
                )

            inavailable_times = list()
            specific_inavailable_time_objects = \
                specific_available_time.objects.filter(
                    teacher_model=the_lesson_info_object.teacher,
                    date__gte=date_function.today()).filter(is_occupied=True)
            
            for each_specific_inavailable_time_object in specific_inavailable_time_objects:
                the_date = str(each_specific_inavailable_time_object.date)
                inavailable_times.append(
                    f'{the_date}:{each_specific_inavailable_time_object.time};'
                )

            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = {
                'availableTime': available_times,
                'bookedTime': inavailable_times
            }

    return JsonResponse(response)
            

@require_http_methods(['POST'])
def booking_lessons(request):
    '''
    學生預約課程的API，進行預約功能前，還必須先確認學生有剩餘時數可供預約。
    {
        status: ‘success’ / ’failed’
        errCode: None
        errMsg: None
        data:[]
    }
    '''
    response = dict()
    student_auth_id = request.POST.get('userID', False)
    lesson_id = request.POST.get('lessonID', False)
    booking_date_time = request.POST.get('bookingDateTime', False)
    # booking_date_time 類似這種形式 >> '2020-11-11:0,1,2,3;2020-11-12:0,1,2,3;'
    
    if not check_if_all_variables_are_true(student_auth_id, lesson_id, booking_date_time):
        # 資料傳輸錯誤
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    else:
        #print(f'student_auth_id: {student_auth_id}')
        #print(f'lesson_id: {lesson_id}')
        #print(f'booking_date_time: {booking_date_time}')

        the_student_object = student_profile.objects.filter(auth_id=student_auth_id).first()
        if the_student_object is None:
            # 該名使用者未註冊或未登入
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，您需要登入我們才有辦法協助安排課程預約唷，\
                                  請點選畫面右上角進行登入或註冊，如果有任何問題請告訴我們，讓我們為您服務。'
            response['data'] = None
        else:
            # 先確認有沒有有效的預約時間，不然白做工
            this_booking_minutes, booking_date_times_dict = \
                booking_date_time_to_minutes_and_cleansing(booking_date_time)
            
            if this_booking_minutes == 0:
                # 沒有有效的預約時段
                response['status'] = 'failed'
                response['errCode'] = '2'
                response['errMsg'] = '不好意思，您似乎沒有點選預約時段，請再次確認一下唷，如果持續發生這個問題，\
                                      請與我們聯繫，讓我們為您服務。'
                response['data'] = booking_date_time

            else:
                # 確實有收到有效的預約時段
                # 先確認一下該用戶目前有沒有可用的 "試教" 預約
                student_available_lesson_sets_ids = \
                    list(student_remaining_minutes_of_each_purchased_lesson_set.objects.values_list(
                        'lesson_sales_set_id', flat=True).filter(
                        student_auth_id=student_auth_id, lesson_id=lesson_id, 
                    ).exclude(available_remaining_minutes=0))
                available_purchased_trial_lesson_sales_sets = \
                    lesson_sales_sets.objects.filter(
                        id__in=student_available_lesson_sets_ids, sales_set='trial').first()
                
                if available_purchased_trial_lesson_sales_sets is None:
                    # 代表使用者沒有尚未使用的試教使用資格，可以進行一般的預約
                    
                    # 接著確認該名使用者有沒有剩餘的時數可供預約
                    the_available_remaining_minutes_object = \
                        student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(student_auth_id=student_auth_id, lesson_id=lesson_id).exclude(available_remaining_minutes=0)
                    # 計算所有剩餘的時數(分鐘)
                    available_remaining_minutes = the_available_remaining_minutes_object.aggregate(Sum('available_remaining_minutes'))['available_remaining_minutes__sum']
                    
                    if available_remaining_minutes is None:
                        # 用戶沒有購買任何課程
                        response['status'] = 'failed'
                        response['errCode'] = '6'
                        response['errMsg'] = f'不好意思，您並未購買相關課程，請重新確認課程購買狀況後再進行預約唷，如果持續出現這個問題請您再告訴我們，謝謝您。'
                        response['data'] = (this_booking_minutes, available_remaining_minutes)
                    
                    elif this_booking_minutes > available_remaining_minutes:
                        # 預約的總時數超過user可動用剩餘時數
                        response['status'] = 'failed'
                        response['errCode'] = '3'
                        response['errMsg'] = f'不好意思，您的剩餘時數不足，總計為{available_remaining_minutes}分鐘(只能預約{int(available_remaining_minutes/30)}堂課)，\
                                            請重新確認預約堂數，或再次訂購課程方案後進行預約唷，謝謝您。'
                        response['data'] = (this_booking_minutes, available_remaining_minutes)
  
                    else:
                        # 時數足夠預約，預約成功後要扣除原本的時數
                        # 除了試教只能使用一次以外(即使不滿30分)
                        # 其他假設有兩個sets分別剩餘25分、100分，預約了120分鐘後，
                        # 應該分別變成0分、5分。

                        student_availbale_purchased_lesson_sets = \
                            student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                                lesson_id=lesson_id,
                                student_auth_id=student_auth_id
                            ).exclude(
                                available_remaining_minutes=0
                            ).order_by('created_time')
                        # 按照剩餘時數，由小到大排序，因為比較少的要先用掉  >> WRONG 2021.01.21
                        # 要按照時間排序，先進先出才對

                        how_many_does_this_booking_minutes_leave = this_booking_minutes

                        for each_set in student_availbale_purchased_lesson_sets:
                            if each_set.available_remaining_minutes >= how_many_does_this_booking_minutes_leave:
                                # 本方案的可動用時數就比本次預約多了，直接扣掉、轉移就完事
                                each_set.available_remaining_minutes -= how_many_does_this_booking_minutes_leave
                                each_set.withholding_minutes += how_many_does_this_booking_minutes_leave
                                how_many_does_this_booking_minutes_leave = 0
                                each_set.save()
                                break # 跳出迴圈
                            else:
                                # 本方案的可動用時數尚不足以扣除本次的預約時數
                                how_many_does_this_booking_minutes_leave -= each_set.available_remaining_minutes
                                # 先把本方案可以扣除的時數從 預約時數扣掉
                                each_set.withholding_minutes += each_set.available_remaining_minutes
                                # 再加進預扣時數裡面
                                each_set.available_remaining_minutes = 0
                                # 最後再把本方案的可動用時數扣掉 >> 因為全部抵用所以歸零
                                each_set.save()
                            
                        
                        # 接下來要更新booking狀態
                        new_booking_info_list = list()
                        for each_date, each_times_list in booking_date_times_dict.items():
                            for each_continuous_time in each_times_list:
                                new_booking_info_list.append(
                                    lesson_booking_info(
                                        lesson_id = lesson_id,
                                        teacher_auth_id = student_availbale_purchased_lesson_sets.first().teacher_auth_id,
                                        student_auth_id = student_auth_id,
                                        booked_by = 'student',
                                        last_changed_by = 'student',
                                        booking_set_id = student_availbale_purchased_lesson_sets.first().lesson_sales_set_id,
                                        remaining_minutes = (available_remaining_minutes - this_booking_minutes),
                                        booking_date_and_time = f'{each_date}:{each_continuous_time};',
                                        booking_start_datetime = turn_first_datetime_string_into_time_format(f'{each_date}:{each_continuous_time};'),
                                        booking_status = 'to_be_confirmed'
                                    ))
                        lesson_booking_info.objects.bulk_create(new_booking_info_list)
                        
                        # 寄出一封通知信給老師,提醒老師要來確認時間
                        email_notification = email_manager()
                        email_notification.send_teacher_when_student_booking_his_lesson(
                            teacher_authID = student_availbale_purchased_lesson_sets.first().teacher_auth_id,
                            student_authID = student_auth_id,
                            lesson_id = lesson_id)


                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = None

                else:
                    # 代表使用者有尚未使用的試教使用資格，必須用完才可以進行一般的預約
                    # 而且需要限制在 30min 內(包含)，因為是試教
                    if this_booking_minutes > 30:
                        # 試教預約超過1個小時
                        response['status'] = 'failed'
                        response['errCode'] = '5'
                        response['errMsg'] = f'不好意思，試教體驗課程最多只能預約一堂唷(但是時數不限)> <，\
                                            請重新確認預約堂數，等體驗課程結束後就可以使用其他方案囉，謝謝您。'
                        response['data'] = this_booking_minutes
                    else:
                        # 進行試教的預約
                        # 先找到試教方案set的id!!!!!!
                        # 將學生的該方案先預扣預約時數，因為是試教，故全部扣除
                        the_target_student_set_of_available_remaining_minutes_of_each_purchased_lesson_set = \
                            student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                                lesson_sales_set_id=available_purchased_trial_lesson_sales_sets.id,
                                student_auth_id=student_auth_id,
                                lesson_id=lesson_id).first()
                        
                        the_target_student_set_of_available_remaining_minutes_of_each_purchased_lesson_set.available_remaining_minutes = 0
                        the_target_student_set_of_available_remaining_minutes_of_each_purchased_lesson_set.withholding_minutes = 30
                        the_target_student_set_of_available_remaining_minutes_of_each_purchased_lesson_set.save()
                        # 將預約後的，可動用時數轉移至預扣時數，並儲存

                        # 接下來要更新booking狀態
                        
                        new_booking_info = lesson_booking_info.objects.create(
                            lesson_id = lesson_id,
                            teacher_auth_id = the_target_student_set_of_available_remaining_minutes_of_each_purchased_lesson_set.teacher_auth_id,
                            student_auth_id = student_auth_id,
                            booked_by = 'student',
                            last_changed_by = 'student',
                            booking_set_id = available_purchased_trial_lesson_sales_sets.id,
                            remaining_minutes = 0,  # 因為是試教
                            booking_date_and_time = f'{[*booking_date_times_dict][0]}:{[*booking_date_times_dict.values()][0][0]};',
                            booking_start_datetime = turn_first_datetime_string_into_time_format(
                                f'{[*booking_date_times_dict][0]}:{[*booking_date_times_dict.values()][0][0]};'
                                ),
                            booking_status = 'to_be_confirmed'
                        )
                        new_booking_info.save()
                        
                        # 寄出一封通知信給老師,提醒老師要來確認時間
                        email_notification = email_manager()
                        email_notification.send_teacher_when_student_booking_his_lesson(
                            teacher_authID = the_target_student_set_of_available_remaining_minutes_of_each_purchased_lesson_set.teacher_auth_id,
                            student_authID = student_auth_id,
                            lesson_id = lesson_id)

                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = new_booking_info.id

    return JsonResponse(response)
            

@require_http_methods(['POST'])
def changing_lesson_booking_status(request):
    '''
    更改課程預約的狀態
    {
        userID:
        bookingID://預約序號  >> (這個是 lesson_booking_info 的ID，切記切記)
        bookingStatus://'confirmed', 'canceled'
    }

    2021.01.07:
        想到還沒有加入，當確認預約後，要將其他衝突時段的預約自動取消掉
    '''
    response = dict()
    user_auth_id = request.POST.get('userID', False)
    lesson_booking_info_id = request.POST.get('bookingID', False)
    lesson_booking_info_status = request.POST.get('bookingStatus', False)

    
    if check_if_all_variables_are_true(user_auth_id, lesson_booking_info_id, lesson_booking_info_status):
        # 檢查一下這個 user_auth_id 應該要屬於老師或是學生，兩者其一
        the_teacher = teacher_profile.objects.filter(auth_id=user_auth_id).first()
        the_student = student_profile.objects.filter(auth_id=user_auth_id).first()
        
        if the_teacher is None and the_student is None:
            # 如果兩者都是 None ，雖然想不出來為什麼會找不到發起人，但這不應該發生
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = user_auth_id
        
        else:
            # 確實有找到用戶，可以進行狀態改變了
            # 先確認有沒有該預約紀錄
            that_lesson_booking_info = \
                lesson_booking_info.objects.filter(id=lesson_booking_info_id).first()
            
            if that_lesson_booking_info is None:
                # 找不到該預約紀錄
                response['status'] = 'failed'
                response['errCode'] = '2'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                response['data'] = lesson_booking_info_id

            else:
                # 有該預約紀錄
                which_one_changes_it = 'student' if the_teacher is None else 'teacher'
                character_to_mandarin = lambda x: '老師' if x=='teacher' else '學生'
                # 為了將上面的英文角色轉成中文
                if lesson_booking_info_status == 'confirmed':
                    # 要怎麼讓 lesson_sets 那邊 +1 呢 > <

                    that_lesson_booking_info.last_changed_by = which_one_changes_it
                    that_lesson_booking_info.booking_status = lesson_booking_info_status
                    that_lesson_booking_info.save()

                    # 接下來，因為預約變成「確認」了，所以我們必須要將 預約時段 更新到老師的時程裡面
                    the_teacher_model_object = \
                        teacher_profile.objects.filter(auth_id=that_lesson_booking_info.teacher_auth_id).first()

                    the_date_string, the_time_string = \
                        that_lesson_booking_info.booking_date_and_time[:-1].split(':')
                    the_date = turn_date_string_into_date_format(the_date_string)
                    
                    specific_available_time.objects.create(
                        teacher_model=the_teacher_model_object,
                        date=the_date,
                        time=the_time_string,
                        is_occupied=True
                    ).save()
                    # 更新確認預約時段完成

                    # 接下來要將其它衝突時段的待確認課程預約取消
                    other_to_be_confirmed_lesson_bookings_of_the_teacher_queryset = \
                        lesson_booking_info.objects.filter(
                            teacher_auth_id = that_lesson_booking_info.teacher_auth_id,
                            booking_status = 'to_be_confirmed',
                            booking_date_and_time__contains = the_date_string,
                        ) # 先選出當天的課程
                    if other_to_be_confirmed_lesson_bookings_of_the_teacher_queryset.count():
                        # 代表有符合條件的預約
                        the_time_string_splited_as_list = the_time_string.split(',')
                        # 如果時段中有跟 the_time_string_splited_as_list 的元素重疊到，就取消
                        for each_booking_info_object in other_to_be_confirmed_lesson_bookings_of_the_teacher_queryset:
                            each_booking_info_object_s_time_splited_as_list = \
                                each_booking_info_object.booking_date_and_time[:-1].split(':')[1].split(',')
                            if any(_ in each_booking_info_object_s_time_splited_as_list for _ in the_time_string_splited_as_list):
                                # 有重疊到，需要拒絕，並返還那些人的預扣時數
                                # 這裡應該要在remark寫上系統婉拒的而非老師婉拒
                                each_booking_info_object.remark = \
                                    f'{date_function.today()} 系統自動取消與預定課程衝突的預約'
                                each_booking_info_object.last_changed_by = 'teacher'
                                each_booking_info_object.booking_status = 'canceled'
                                each_booking_info_object.save()
                                # 接下來要確認一下是否為 試教
                                if lesson_sales_sets.objects.filter(
                                    id=each_booking_info_object.booking_set_id
                                    ).first().sales_set == 'trial':
                                    # 是試教

                                    student_remaining_minutes_trial_object = \
                                        student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                                            lesson_id=each_booking_info_object.lesson_id,
                                            lesson_sales_set_id=each_booking_info_object.booking_set_id,
                                            available_remaining_minutes=0
                                        ).first()  # 因為理論上一門課只會有一門試教，所以可以直接拿 first，且其 available_remaining_minutes 必為 0

                                    student_remaining_minutes_trial_object.available_remaining_minutes = \
                                        student_remaining_minutes_trial_object.withholding_minutes
                                    student_remaining_minutes_trial_object.withholding_minutes= 0
                                    student_remaining_minutes_trial_object.save()
                                else:
                                    # 不是試教，因此是什麼方案都無所謂了
                                    # 接下來篩選出非試教的方案們
                                    non_trial_this_lesson_sales_set_ids = \
                                        list(lesson_sales_sets.objects.values_list('id', flat=True).filter(
                                            lesson_id=each_booking_info_object.lesson_id
                                        ).exclude(sales_set='trial'))

                                    student_remaining_minutes_non_trial_objects = \
                                        student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                                            lesson_id=each_booking_info_object.lesson_id,
                                            lesson_sales_set_id__in=non_trial_this_lesson_sales_set_ids,
                                        ).exclude(withholding_minutes=0).order_by('-last_changed_time')

                                    this_booked_times_in_minutes = booking_date_time_to_minutes_and_cleansing(
                                        each_booking_info_object.booking_date_and_time
                                    )[0]

                                    how_many_does_this_booked_times_in_minutes_leave = this_booked_times_in_minutes

                                    for each_student_remaining_minutes_non_trial_object in student_remaining_minutes_non_trial_objects:
                                        # 先確認當前資料的預扣額度能不能補回預約取消的時數
                                        if each_student_remaining_minutes_non_trial_object.withholding_minutes > how_many_does_this_booked_times_in_minutes_leave:
                                            # 如果該方案的預扣額度可以直接補回取消的時數
                                            each_student_remaining_minutes_non_trial_object.available_remaining_minutes += \
                                                how_many_does_this_booked_times_in_minutes_leave
                                            each_student_remaining_minutes_non_trial_object.withholding_minutes -= \
                                                how_many_does_this_booked_times_in_minutes_leave
                                            how_many_does_this_booked_times_in_minutes_leave = 0
                                            each_student_remaining_minutes_non_trial_object.save()
                                            break
                                        else:
                                            # 無法完全補回，先補回所有的預扣時數，接著再依靠下一筆資料
                                            each_student_remaining_minutes_non_trial_object.available_remaining_minutes += \
                                                each_student_remaining_minutes_non_trial_object.withholding_minutes
                                            how_many_does_this_booked_times_in_minutes_leave -= \
                                                each_student_remaining_minutes_non_trial_object.withholding_minutes
                                            each_student_remaining_minutes_non_trial_object.withholding_minutes = 0
                                            each_student_remaining_minutes_non_trial_object.save()
                                
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                    response['data'] = None

                elif lesson_booking_info_status == 'canceled':
                    # 除了更改狀態以外，也要記得將預扣時數返還
                    # 除此之外，也需要將老師原本已經確認預約的時段取消、變成空閒時段

                    # 這裡要確認一下在 canceled 之前，究竟是雙方都確認預約了 >> 此時是取消預約  
                    # 或是其中一方發送預約邀請  >>  此時是婉拒預約

                    if that_lesson_booking_info.booking_status == 'confirmed':
                        that_lesson_booking_info.remark = \
                            f'{date_function.today()} {character_to_mandarin(which_one_changes_it)}取消預定課程'
                    elif that_lesson_booking_info.booking_status == 'to_be_confirmed':
                        that_lesson_booking_info.remark = \
                            f'{date_function.today()} {character_to_mandarin(which_one_changes_it)}婉拒預約'
                    that_lesson_booking_info.last_changed_by = which_one_changes_it
                    that_lesson_booking_info.booking_status = lesson_booking_info_status
                    that_lesson_booking_info.save()

                    # 接下來要確認一下是否為 試教
                    if lesson_sales_sets.objects.filter(
                        id=that_lesson_booking_info.booking_set_id
                        ).first().sales_set == 'trial':
                        # 是試教

                        student_remaining_minutes_trial_object = \
                            student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                                lesson_id=that_lesson_booking_info.lesson_id,
                                lesson_sales_set_id=that_lesson_booking_info.booking_set_id,
                                available_remaining_minutes=0
                            ).first()  # 因為理論上一門課只會有一門試教，所以可以直接拿 first，且其 available_remaining_minutes 必為 0

                        student_remaining_minutes_trial_object.available_remaining_minutes = \
                            student_remaining_minutes_trial_object.withholding_minutes
                        student_remaining_minutes_trial_object.withholding_minutes= 0
                        student_remaining_minutes_trial_object.save()

                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = None
                    
                    else:
                        # 不是試教，因此是什麼方案都無所謂了
                        # 接下來篩選出非試教的方案們
                        non_trial_this_lesson_sales_set_ids = \
                            list(lesson_sales_sets.objects.values_list('id', flat=True).filter(
                                lesson_id=that_lesson_booking_info.lesson_id
                            ).exclude(sales_set='trial'))

                        student_remaining_minutes_non_trial_objects = \
                            student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                                lesson_id=that_lesson_booking_info.lesson_id,
                                lesson_sales_set_id__in=non_trial_this_lesson_sales_set_ids,
                            ).exclude(withholding_minutes=0).order_by('-last_changed_time')

                        this_booked_times_in_minutes = booking_date_time_to_minutes_and_cleansing(
                            that_lesson_booking_info.booking_date_and_time
                        )[0]

                        how_many_does_this_booked_times_in_minutes_leave = this_booked_times_in_minutes

                        for each_student_remaining_minutes_non_trial_object in student_remaining_minutes_non_trial_objects:
                            # 先確認當前資料的預扣額度能不能補回預約取消的時數
                            if each_student_remaining_minutes_non_trial_object.withholding_minutes > how_many_does_this_booked_times_in_minutes_leave:
                                # 如果該方案的預扣額度可以直接補回取消的時數
                                each_student_remaining_minutes_non_trial_object.available_remaining_minutes += \
                                    how_many_does_this_booked_times_in_minutes_leave
                                each_student_remaining_minutes_non_trial_object.withholding_minutes -= \
                                    how_many_does_this_booked_times_in_minutes_leave
                                how_many_does_this_booked_times_in_minutes_leave = 0
                                each_student_remaining_minutes_non_trial_object.save()
                                break
                            else:
                                # 無法完全補回，先補回所有的預扣時數，接著再依靠下一筆資料
                                each_student_remaining_minutes_non_trial_object.available_remaining_minutes += \
                                    each_student_remaining_minutes_non_trial_object.withholding_minutes
                                how_many_does_this_booked_times_in_minutes_leave -= \
                                    each_student_remaining_minutes_non_trial_object.withholding_minutes
                                each_student_remaining_minutes_non_trial_object.withholding_minutes = 0
                                each_student_remaining_minutes_non_trial_object.save()
                        
                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = None

                    # 不論是不是試教，取消教師 已預約時段 的流程都不會改變，故統一在這裡做
                    the_teacher_model_object = \
                        teacher_profile.objects.filter(auth_id=that_lesson_booking_info.teacher_auth_id).first()
                    booked_date_time_dict = \
                        booking_date_time_to_minutes_and_cleansing(
                            that_lesson_booking_info.booking_date_and_time
                        )[1]
                    # 接下來刪掉 該教師對應的已預約的時段
                    # print(f'booked_date_time_dict 11 {booked_date_time_dict}')
                    for each_date, each_time_list in booked_date_time_dict.items():
                        for each_time in each_time_list:        
                            specific_available_time.objects.filter(
                                teacher_model=the_teacher_model_object,
                                date=turn_date_string_into_date_format(each_date),
                                time=each_time
                            ).delete()


    else:
        # 沒有收到前端的資料
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)


@require_http_methods(['POST'])
def get_student_s_available_remaining_minutes(request):
    response = dict()
    none_to_zero = lambda x: 0 if x is None else x

    student_auth_id = request.POST.get('userID', False)
    lesson_id = request.POST.get('lessonID', False)

    if check_if_all_variables_are_true(student_auth_id, lesson_id):

        all_available_remaining_minutes_queryset = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                lesson_id=lesson_id,
                student_auth_id=student_auth_id).exclude(
                    available_remaining_minutes=0)

        all_trial_sales_sets_of_this_lesson_query_set = \
            lesson_sales_sets.objects.filter(
                lesson_id=lesson_id, sales_set='trial')

        student_all_available_set_ids = \
            all_available_remaining_minutes_queryset.values_list('lesson_sales_set_id', flat=True)
        
        all_trial_set_ids_of_the_lesson = \
                all_trial_sales_sets_of_this_lesson_query_set.values_list('id', flat=True)
        
        if any(_ in all_trial_set_ids_of_the_lesson for _ in student_all_available_set_ids):
            # 任何一筆有重疊，代表user有未使用的該門課程的試教方案
            student_has_unused_trial_lesson_sales_set = True
            all_available_remaining_minutes_of_this_lesson = \
                    all_available_remaining_minutes_queryset.aggregate(Sum('available_remaining_minutes'))['available_remaining_minutes__sum']
            
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = {
                'all_available_remaining_minutes_of_this_lesson': all_available_remaining_minutes_of_this_lesson,
                'student_has_unused_trial_lesson_sales_set': student_has_unused_trial_lesson_sales_set}
        
        else:
            # 代表 user 沒有未使用的該門課程的試教方案
            student_has_unused_trial_lesson_sales_set = False
            all_available_remaining_minutes_of_this_lesson = none_to_zero(
                all_available_remaining_minutes_queryset.aggregate(Sum('available_remaining_minutes'))['available_remaining_minutes__sum'])
            
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = {
                'all_available_remaining_minutes_of_this_lesson': all_available_remaining_minutes_of_this_lesson,
                'student_has_unused_trial_lesson_sales_set': student_has_unused_trial_lesson_sales_set}


    else:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)


@require_http_methods(['POST'])
def get_teacher_s_booking_history(request):
    '''
    回傳該名老師所有預約、課程的狀態。
    接收：
    {
        userID (teacher_auth_id)
        searched_by: string 只能搜尋學生姓名(暱稱)或課程title
        filtered_by: string // 依照什麼做篩選 _狀態
                字串顯示：
                        /預約成功（confirmed）
                        /待回覆（to_be_confirmed）
                        /已完課（finished）
                        /已取消（canceled）
        registered_from_date//起始日期2020-01-01  若為空字串，則預設左邊 
        registered_to_date//結束日期2050-12-31   若為空字串，則預設左邊 
    }
    回傳：
    {
        status: “success“ / “failed“ 
        errCode: None 
        errMsg: None
        data:[
            {
                booked_date：預約日期，如1990-01-01,
                booked_time：預約時間以陣列代碼顯示，如['10', '11'], *只能是連續的代碼
                booked_status: 預約狀態: 預約成功、待回覆...
                                        /預約成功（confirmed）
                                        /待回覆（to_be_confirmed）
                                        /已完課（finished）
                                            加上下面兩個小分類 >>
                                            / 學生確認時數中  student_not_yet_confirmed
                                            / 學生反對該時數，客服處理中  quikok_dealing_for_student_disagreed
                                        /已取消（canceled）
                lesson_title: 預約課程名稱,
                student_auth_id: 學生的auth_id,
                student_thumbnail_path: 學生的大頭貼路徑,
                student_nickname: 學生暱稱,
                discount_price:  課程方案，
                                    如:'trial'(試課優惠)
                                        /'no_discount'(單堂原價)
                                        /'HH:XX'(HH小時XX折)
                remaining_time：學生購買剩餘時數

                新增 >>
                lesson_booking_info_id:  預約的id
                teacher_declared_start_time: xx:xx    老師宣稱的上課起時始間
                teacher_declared_end_time: xx:xx    老師宣稱的上課結束始間
                teacher_declared_time_in_minutes:  xx 老師宣稱的上課時數(分鐘)
                student_confirmed_deadline:  學生的確認截止日(當天可) "xxxx-xx-xx"
                remark: 加上課程被取消的理由或原因，如：【xxxx-xx-xx xx:xx 老師1號取消】，若無取消則為null
                is_teacher_given_feedback: (布林值: 老師送出時數後，老師是否有針對該課程給出評價；若未送出時數則為null)
                is_student_given_feedback: (布林值: 老師送出時數後，學生是否有針對該課程給出評價；若未送出時數則為null)
            }
        ]
    }
    '''
    response = dict()
    teacher_auth_id = request.POST.get('userID', False)
    booking_status_filtered_by = request.POST.get('filtered_by', False)
    searched_by = request.POST.get('searched_by', False)
    registered_from_date = request.POST.get('registered_from_date', False)
    registered_to_date = request.POST.get('registered_to_date', False)

    if check_if_all_variables_are_true(teacher_auth_id, booking_status_filtered_by, searched_by,
        registered_from_date, registered_to_date):
        # 有正確收到資料
        # 因為 registered_from_date 跟 registered_to_date 有可能是空字串，所以另外處理
        if len(registered_from_date):
            registered_from_date = date_string_2_dateformat(registered_from_date)
        else:
            registered_from_date = date_string_2_dateformat('2020-01-01')

        if len(registered_to_date):
            registered_to_date = date_string_2_dateformat(registered_to_date)
        else:
            registered_to_date = date_string_2_dateformat('2050-12-31')

        teacher_object = teacher_profile.objects.filter(auth_id=teacher_auth_id).first()
        
        if teacher_object is None:
            # 這位老師不存在
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = teacher_auth_id

        else:
            # 確實有找到這位老師
            # 先看看他的 lesson_booking_info，這裡先過濾篩選條件，避免每次都query一堆東西造成效能問題
            if len(booking_status_filtered_by):
                # 代表 booking_status_filtered_by 有東西，user有輸入搜尋條件
                # 輸入 finished 的話，需要另外抓出
                #       1. student_not_yet_confirmed
                #       2. quikok_dealing_for_student_disagreed
                # 當作一樣是finished項目下的內容

                # 檢查 user有沒有輸入 searched_by 條件搜尋學生姓名/暱稱 或是 課程名稱
                if len(searched_by.strip()):
                    searched_by = searched_by.strip()
                    # 有輸入 searched_by
                    correspodent_student_auth_ids = \
                        list(student_profile.objects.values_list('auth_id', flat=True).filter(
                            Q(name__contains=searched_by) | Q(nickname__contains=searched_by)
                        ))
                    correspodent_lesson_ids = \
                        list(lesson_info.objects.values_list('id', flat=True).filter(
                            lesson_title__contains=searched_by))
                    
                    if booking_status_filtered_by != 'finished':
                        teacher_s_lesson_booking_info_queryset = \
                            lesson_booking_info.objects.filter(
                                Q(teacher_auth_id=teacher_auth_id) & 
                                Q(booking_status=booking_status_filtered_by) & 
                                Q(created_time__gt=registered_from_date) &
                                Q(last_changed_time__lt=registered_to_date)).filter(
                                    Q(student_auth_id__in=correspodent_student_auth_ids) |
                                    Q(lesson_id__in=correspodent_lesson_ids)
                                ).order_by('-last_changed_time')
                    else:
                        teacher_s_lesson_booking_info_queryset = \
                            lesson_booking_info.objects.filter(
                                Q(teacher_auth_id=teacher_auth_id) & 
                                Q(booking_status__in=['finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed']) & 
                                Q(created_time__gt=registered_from_date) &
                                Q(last_changed_time__lt=registered_to_date)).filter(
                                    Q(student_auth_id__in=correspodent_student_auth_ids) |
                                    Q(lesson_id__in=correspodent_lesson_ids)
                                ).order_by('-last_changed_time')
                else:
                    # 沒有輸入 searched_by
                    if booking_status_filtered_by != 'finished':
                        teacher_s_lesson_booking_info_queryset = \
                            lesson_booking_info.objects.filter(
                                Q(teacher_auth_id=teacher_auth_id) & 
                                Q(booking_status=booking_status_filtered_by) & 
                                Q(created_time__gt=registered_from_date) &
                                Q(last_changed_time__lt=registered_to_date)).order_by('-last_changed_time')
                    else:
                        teacher_s_lesson_booking_info_queryset = \
                            lesson_booking_info.objects.filter(
                                Q(teacher_auth_id=teacher_auth_id) & 
                                Q(booking_status__in=['finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed']) & 
                                Q(created_time__gt=registered_from_date) &
                                Q(last_changed_time__lt=registered_to_date)).order_by('-last_changed_time')
                
                if teacher_s_lesson_booking_info_queryset.count() == 0:
                    # 這個老師什麼預約歷史都沒有
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                    response['data'] = list()
                else:
                    # 這個老師 非 什麼預約歷史都沒有
                    response['data'] = list()
                    for each_booking_info_object in teacher_s_lesson_booking_info_queryset:
                        corr_lesson_completed_record_object = \
                            lesson_completed_record.objects.filter(lesson_booking_info_id=each_booking_info_object.id).first()
                        
                        if corr_lesson_completed_record_object is None:
                            # 這門課還沒有完課的紀錄
                            teacher_declared_start_time = ''
                            teacher_declared_end_time = ''
                            teacher_declared_time_in_minutes = ''
                            student_confirmed_deadline = ''
                            is_teacher_given_feedback = None
                            is_student_given_feedback = None
                        else:
                            # 這門課已完課
                            # 所以評價狀態應該只有 True 或 False 兩種狀態
                            lesson_reviews_from_students_object = \
                                lesson_reviews_from_students.objects.filter(
                                    corresponding_lesson_booking_info_id=each_booking_info_object.id
                                    ).first()  # 學生對老師的評論紀錄

                            student_reviews_from_teachers_object = \
                                student_reviews_from_teachers.objects.filter(
                                    corresponding_lesson_booking_info_id=each_booking_info_object.id
                                    ).first()  # 老師對學生的評論紀錄

                            teacher_declared_start_time = \
                                corr_lesson_completed_record_object.teacher_declared_start_time.strftime("%H:%M")
                            teacher_declared_end_time = \
                                corr_lesson_completed_record_object.teacher_declared_end_time.strftime("%H:%M")
                            teacher_declared_time_in_minutes = \
                                corr_lesson_completed_record_object.teacher_declared_time_in_minutes
                            student_confirmed_deadline = \
                                 corr_lesson_completed_record_object.student_confirmed_deadline
                            is_teacher_given_feedback = False if student_reviews_from_teachers_object is None else True
                            is_student_given_feedback = False if lesson_reviews_from_students_object is None else True
                        
                        student_object = \
                            student_profile.objects.get(auth_id=each_booking_info_object.student_auth_id)

                        response['data'].append(
                            {
                                'booked_date': each_booking_info_object.booking_date_and_time.split(':')[0],
                                'booked_time': each_booking_info_object.booking_date_and_time.split(':')[1][:-1].split(','),
                                # [:-1]是為了去掉最後的 ';'
                                'booked_status': each_booking_info_object.booking_status,
                                'lesson_title': \
                                    lesson_info.objects.get(id=each_booking_info_object.lesson_id).lesson_title,
                                'student_auth_id': \
                                    each_booking_info_object.student_auth_id,
                                'student_nickname': student_object.nickname,
                                'student_thumbnail_path': student_object.thumbnail_dir,
                                'discount_price': \
                                    lesson_sales_sets.objects.get(id=each_booking_info_object.booking_set_id).sales_set,
                                'remaining_time': each_booking_info_object.remaining_minutes,
                                'lesson_booking_info_id': each_booking_info_object.id,
                                'teacher_declared_start_time': teacher_declared_start_time,
                                'teacher_declared_end_time': teacher_declared_end_time,
                                'teacher_declared_time_in_minutes': teacher_declared_time_in_minutes,
                                'student_confirmed_deadline': student_confirmed_deadline,
                                'remark': each_booking_info_object.remark,
                                # 【xxxx-xx-xx xx:xx 老師1號取消】，若無取消則為null，暫時先跳過
                                'is_teacher_given_feedback': is_teacher_given_feedback,
                                'is_student_given_feedback': is_student_given_feedback
                            }
                        )
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None

            else:
                # 代表 booking_status_filtered_by 沒東西，user無輸入搜尋條件，傳回所有資訊

                # 檢查 user有沒有輸入 searched_by 條件搜尋學生姓名/暱稱 或是 課程名稱
                if len(searched_by.strip()):
                    searched_by = searched_by.strip()
                    # 有輸入 searched_by
                    correspodent_student_auth_ids = \
                        list(student_profile.objects.values_list('auth_id', flat=True).filter(
                            Q(name__contains=searched_by) | Q(nickname__contains=searched_by)
                        ))
                    correspodent_lesson_ids = \
                        list(lesson_info.objects.values_list('id', flat=True).filter(
                            lesson_title__contains=searched_by
                        ))

                    teacher_s_lesson_booking_info_queryset = \
                        lesson_booking_info.objects.filter(
                            Q(teacher_auth_id=teacher_auth_id) & 
                            Q(created_time__gt=registered_from_date) &
                            Q(last_changed_time__lt=registered_to_date)).filter(
                                Q(student_auth_id__in=correspodent_student_auth_ids) |
                                Q(lesson_id__in=correspodent_lesson_ids)
                            ).order_by('-last_changed_time')
                else:
                    # 有輸入 searched_by
                    teacher_s_lesson_booking_info_queryset = \
                        lesson_booking_info.objects.filter(
                            teacher_auth_id=teacher_auth_id, 
                            created_time__gt=registered_from_date,
                            last_changed_time__lt=registered_to_date).order_by('-last_changed_time')
                
                
                if teacher_s_lesson_booking_info_queryset.count() == 0:
                    # 這個老師什麼預約歷史都沒有
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                    response['data'] = list()
                else:
                    # 這個老師 非 什麼預約歷史都沒有
                    response['data'] = list()
                    for each_booking_info_object in teacher_s_lesson_booking_info_queryset:
                        corr_lesson_completed_record_object = \
                            lesson_completed_record.objects.filter(lesson_booking_info_id=each_booking_info_object.id).first()
                        
                        if corr_lesson_completed_record_object is None:
                            # 這門課還沒有完課的紀錄
                            teacher_declared_start_time = ''
                            teacher_declared_end_time = ''
                            teacher_declared_time_in_minutes = ''
                            student_confirmed_deadline = ''
                            is_teacher_given_feedback = None
                            is_student_given_feedback = None
                            # 因為沒有完課，所以一定不會有評價
                        else:
                            # 這門課已完課
                            # 所以評價狀態應該只有 True 或 False 兩種狀態
                            lesson_reviews_from_students_object = \
                                lesson_reviews_from_students.objects.filter(
                                    corresponding_lesson_booking_info_id=each_booking_info_object.id
                                    ).first()  # 學生對老師的評論紀錄

                            student_reviews_from_teachers_object = \
                                student_reviews_from_teachers.objects.filter(
                                    corresponding_lesson_booking_info_id=each_booking_info_object.id
                                    ).first()  # 老師對學生的評論紀錄

                            teacher_declared_start_time = \
                                corr_lesson_completed_record_object.teacher_declared_start_time.strftime("%H:%M")
                            teacher_declared_end_time = \
                                corr_lesson_completed_record_object.teacher_declared_end_time.strftime("%H:%M")
                            teacher_declared_time_in_minutes = \
                                corr_lesson_completed_record_object.teacher_declared_time_in_minutes
                            student_confirmed_deadline = \
                                 corr_lesson_completed_record_object.student_confirmed_deadline
                            is_teacher_given_feedback = False if student_reviews_from_teachers_object is None else True
                            is_student_given_feedback = False if lesson_reviews_from_students_object is None else True

                        student_object = \
                            student_profile.objects.get(auth_id=each_booking_info_object.student_auth_id)
                        
                        response['data'].append(
                            {
                                'booked_date': each_booking_info_object.booking_date_and_time.split(':')[0],
                                'booked_time': each_booking_info_object.booking_date_and_time.split(':')[1][:-1].split(','),
                                # 去掉最後的 ';'
                                'booked_status': each_booking_info_object.booking_status,
                                'lesson_title': \
                                    lesson_info.objects.get(id=each_booking_info_object.lesson_id).lesson_title,
                                'student_auth_id': \
                                    each_booking_info_object.student_auth_id,
                                'student_nickname': student_object.nickname,
                                'student_thumbnail_path': student_object.thumbnail_dir,
                                'discount_price': \
                                    lesson_sales_sets.objects.get(id=each_booking_info_object.booking_set_id).sales_set,
                                'remaining_time': each_booking_info_object.remaining_minutes,
                                'lesson_booking_info_id': each_booking_info_object.id,
                                'teacher_declared_start_time': teacher_declared_start_time,
                                'teacher_declared_end_time': teacher_declared_end_time,
                                'teacher_declared_time_in_minutes': teacher_declared_time_in_minutes,
                                'student_confirmed_deadline': student_confirmed_deadline,
                                'remark': each_booking_info_object.remark, 
                                # 【xxxx-xx-xx xx:xx 老師1號取消】，若無取消則為null，暫時先跳過
                                'is_teacher_given_feedback': is_teacher_given_feedback,
                                'is_student_given_feedback': is_student_given_feedback
                            }
                        )
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None

    else:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)
    

@require_http_methods(['POST'])
def get_student_s_booking_history(request):
    '''
    回傳該名學生所有預約、課程的狀態。
    接收：
    {
        userID (student_auth_id)
        searched_by: string 只能搜尋老師姓名(暱稱)或課程title
        filtered_by: string // 依照什麼做篩選 _狀態
                字串顯示：
                        /預約成功（confirmed）
                        /待回覆（to_be_confirmed）
                        /已完課（finished）
                        /已取消（canceled）
        registered_from_date//起始日期2020-01-01  若為空字串，則預設左邊 
        registered_to_date//結束日期2050-12-31   若為空字串，則預設左邊 
    }
    回傳：
    {
        status: “success“ / “failed“ 
        errCode: None 
        errMsg: None
        data:[
            {
                booked_date：預約日期，如1990-01-01,
                booked_time：預約時間以陣列代碼顯示，如['10', '11'], *只能是連續的代碼
                booked_status: 預約狀態: 預約成功、待回覆...
                                        /預約成功（confirmed）
                                        /待回覆（to_be_confirmed）
                                        /已完課（finished）
                                            加上下面兩個小分類 >>
                                            / 學生確認時數中  student_not_yet_confirmed
                                            / 學生反對該時數，客服處理中  quikok_dealing_for_student_disagreed
                                        /已取消（canceled）
                lesson_title: 預約課程名稱,
                teacher_auth_id: 老師的auth_id
                teacher_nickname: 老師暱稱,
                teacher_thumbnail_path: 老師大頭貼路徑,
                discount_price:  課程方案，
                                    如:'trial'(試課優惠)
                                        /'no_discount'(單堂原價)
                                        /'HH:XX'(HH小時XX折)
                remaining_time：學生購買剩餘時數

                新增 >>
                lesson_booking_info_id:  預約的id
                teacher_declared_start_time: xx:xx    老師宣稱的上課起時始間
                teacher_declared_end_time: xx:xx    老師宣稱的上課結束始間
                teacher_declared_time_in_minutes:  xx 老師宣稱的上課時數(分鐘)
                student_confirmed_deadline:  學生的確認截止日(當天可) "xxxx-xx-xx"
                remark: 加上課程被取消的理由或原因，如：【xxxx-xx-xx xx:xx 老師1號取消】，若無取消則為null
                is_teacher_given_feedback: (布林值: 老師送出時數後，老師是否有針對該課程給出評價；若未送出時數則為null)
                is_student_given_feedback: (布林值: 老師送出時數後，學生是否有針對該課程給出評價；若未送出時數則為null)
            }
        ]
    }
    '''
    response = dict()
    student_auth_id = request.POST.get('userID', False)
    searched_by = request.POST.get('searched_by', False)
    booking_status_filtered_by = request.POST.get('filtered_by', False)
    registered_from_date = request.POST.get('registered_from_date', False)
    registered_to_date = request.POST.get('registered_to_date', False)

    if check_if_all_variables_are_true(student_auth_id, booking_status_filtered_by, 
        registered_from_date, registered_to_date, searched_by):
        # 有正確收到資料
        # 因為 registered_from_date 跟 registered_to_date 有可能是空字串，所以另外處理
        if len(registered_from_date):
            registered_from_date = date_string_2_dateformat(registered_from_date)
        else:
            registered_from_date = date_string_2_dateformat('2020-01-01')

        if len(registered_to_date):
            registered_to_date = date_string_2_dateformat(registered_to_date)
        else:
            registered_to_date = date_string_2_dateformat('2050-12-31')

        student_object = student_profile.objects.filter(auth_id=student_auth_id).first()
        
        if student_object is None:
            # 這位學生不存在
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = student_auth_id

        else:
            # 確實有找到這位學生
            # 先看看他的 lesson_booking_info，這裡先過濾篩選條件，避免每次都query一堆東西造成效能問題
            if len(booking_status_filtered_by):
                # 代表 booking_status_filtered_by 有東西，user有輸入搜尋條件

                # 檢查 user有沒有輸入 searched_by 條件搜尋老師姓名/暱稱 或是 課程名稱
                if len(searched_by.strip()):
                    searched_by = searched_by.strip()
                    # 有輸入 searched_by
                    correspodent_teacher_auth_ids = \
                        list(teacher_profile.objects.values_list('auth_id', flat=True).filter(
                            Q(name__contains=searched_by) | Q(nickname__contains=searched_by)
                        ))
                    correspodent_lesson_ids = \
                        list(lesson_info.objects.values_list('id', flat=True).filter(
                            lesson_title__contains=searched_by
                        ))

                    if booking_status_filtered_by != 'finished':
                        student_s_lesson_booking_info_queryset = \
                            lesson_booking_info.objects.filter(
                                Q(student_auth_id=student_auth_id) & 
                                Q(booking_status=booking_status_filtered_by) & 
                                Q(created_time__gt=registered_from_date) &
                                Q(last_changed_time__lt=registered_to_date)).filter(
                                    Q(teacher_auth_id__in=correspodent_teacher_auth_ids) |
                                    Q(lesson_id__in=correspodent_lesson_ids)
                                ).order_by('-last_changed_time')
                        #print(f'THIS SHOULD BE ACTIVATED, {student_s_lesson_booking_info_queryset.count()}')
                        #print(f'booking_status_filtered_by, {booking_status_filtered_by}')
                        #print(f'registered_from_date, {registered_from_date}')
                        #print(f'last_changed_time__lt, {registered_to_date}')
                    else:
                        student_s_lesson_booking_info_queryset = \
                            lesson_booking_info.objects.filter(
                                Q(student_auth_id=student_auth_id) & 
                                Q(booking_status__in=['finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed']) & 
                                Q(created_time__gt=registered_from_date) &
                                Q(last_changed_time__lt=registered_to_date)).filter(
                                    Q(teacher_auth_id__in=correspodent_teacher_auth_ids) |
                                    Q(lesson_id__in=correspodent_lesson_ids)
                                ).order_by('-last_changed_time')

                else:
                    # 沒有輸入 searched_by
                    if booking_status_filtered_by != 'finished':
                        student_s_lesson_booking_info_queryset = \
                            lesson_booking_info.objects.filter(
                                Q(student_auth_id=student_auth_id) & 
                                Q(booking_status=booking_status_filtered_by) & 
                                Q(created_time__gt=registered_from_date) &
                                Q(last_changed_time__lt=registered_to_date)).order_by('-last_changed_time')
                    else:
                        student_s_lesson_booking_info_queryset = \
                            lesson_booking_info.objects.filter(
                                Q(student_auth_id=student_auth_id) & 
                                Q(booking_status__in=['finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed']) & 
                                Q(created_time__gt=registered_from_date) &
                                Q(last_changed_time__lt=registered_to_date)).order_by('-last_changed_time')

                if student_s_lesson_booking_info_queryset.count() == 0:
                    # 這個學生什麼預約歷史都沒有
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                    response['data'] = list()
                else:
                    # 這個學生 非 什麼預約歷史都沒有
                    response['data'] = list()
                    for each_booking_info_object in student_s_lesson_booking_info_queryset:
                        
                        corr_lesson_completed_record_object = \
                            lesson_completed_record.objects.filter(lesson_booking_info_id=each_booking_info_object.id).first()
                        
                        if corr_lesson_completed_record_object is None:
                            # 這門課還沒有完課的紀錄
                            teacher_declared_start_time = ''
                            teacher_declared_end_time = ''
                            teacher_declared_time_in_minutes = ''
                            student_confirmed_deadline = ''
                            is_teacher_given_feedback = None
                            is_student_given_feedback = None
                        else:
                            # 這門課已完課
                            # 所以評價狀態應該只有 True 或 False 兩種狀態
                            lesson_reviews_from_students_object = \
                                lesson_reviews_from_students.objects.filter(
                                    corresponding_lesson_booking_info_id=each_booking_info_object.id
                                    ).first()  # 學生對老師的評論紀錄

                            student_reviews_from_teachers_object = \
                                student_reviews_from_teachers.objects.filter(
                                    corresponding_lesson_booking_info_id=each_booking_info_object.id
                                    ).first()  # 老師對學生的評論紀錄

                            teacher_declared_start_time = \
                                corr_lesson_completed_record_object.teacher_declared_start_time.strftime("%H:%M")
                            teacher_declared_end_time = \
                                corr_lesson_completed_record_object.teacher_declared_end_time.strftime("%H:%M")
                            teacher_declared_time_in_minutes = \
                                corr_lesson_completed_record_object.teacher_declared_time_in_minutes
                            student_confirmed_deadline = \
                                 corr_lesson_completed_record_object.student_confirmed_deadline
                            is_teacher_given_feedback = False if student_reviews_from_teachers_object is None else True
                            is_student_given_feedback = False if lesson_reviews_from_students_object is None else True
                        
                        teacher_object = \
                            teacher_profile.objects.get(auth_id=each_booking_info_object.teacher_auth_id)

                        response['data'].append(
                            {
                                'booked_date': each_booking_info_object.booking_date_and_time.split(':')[0],
                                'booked_time': each_booking_info_object.booking_date_and_time.split(':')[1][:-1].split(','),
                                # [:-1]是為了去掉最後的 ';'
                                'booked_status': each_booking_info_object.booking_status,
                                'lesson_title': \
                                    lesson_info.objects.get(id=each_booking_info_object.lesson_id).lesson_title,
                                'teacher_auth_id': \
                                    each_booking_info_object.teacher_auth_id,
                                'teacher_nickname': teacher_object.nickname,
                                'teacher_thumbnail_path': teacher_object.thumbnail_dir,
                                'discount_price': \
                                    lesson_sales_sets.objects.get(id=each_booking_info_object.booking_set_id).sales_set,
                                'remaining_time': each_booking_info_object.remaining_minutes,
                                'lesson_booking_info_id': each_booking_info_object.id,
                                'teacher_declared_start_time': teacher_declared_start_time,
                                'teacher_declared_end_time': teacher_declared_end_time,
                                'teacher_declared_time_in_minutes': teacher_declared_time_in_minutes,
                                'student_confirmed_deadline': student_confirmed_deadline,
                                'remark': each_booking_info_object.remark,
                                'is_teacher_given_feedback': is_teacher_given_feedback,
                                'is_student_given_feedback': is_student_given_feedback
                            }
                        )
                        
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None

            else:
                # 代表 booking_status_filtered_by 沒東西，user無輸入搜尋條件，傳回所有資訊
                # 檢查 user有沒有輸入 searched_by 條件搜尋老師姓名/暱稱 或是 課程名稱
                if len(searched_by.strip()):
                    searched_by = searched_by.strip()
                    # 有輸入 searched_by
                    correspodent_teacher_auth_ids = \
                        list(teacher_profile.objects.values_list('auth_id', flat=True).filter(
                            Q(name__contains=searched_by) | Q(nickname__contains=searched_by)
                        ))
                    correspodent_lesson_ids = \
                        list(lesson_info.objects.values_list('id', flat=True).filter(
                            lesson_title__contains=searched_by
                        ))

                    student_s_lesson_booking_info_queryset = \
                        lesson_booking_info.objects.filter(
                            Q(student_auth_id=student_auth_id) & 
                            Q(created_time__gt=registered_from_date) &
                            Q(last_changed_time__lt=registered_to_date)).filter(
                                Q(teacher_auth_id__in=correspodent_teacher_auth_ids) |
                                Q(lesson_id__in=correspodent_lesson_ids)
                            ).order_by('-last_changed_time')
                else:
                    # 沒有輸入 searched_by
                    student_s_lesson_booking_info_queryset = \
                        lesson_booking_info.objects.filter(
                            student_auth_id=student_auth_id, 
                            created_time__gt=registered_from_date,
                            last_changed_time__lt=registered_to_date).order_by('-last_changed_time')
                
                if student_s_lesson_booking_info_queryset.count() == 0:
                    # 這個學生什麼預約歷史都沒有
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                    response['data'] = list()
                else:
                    # 這個學生 非 什麼預約歷史都沒有
                    response['data'] = list()
                    for each_booking_info_object in student_s_lesson_booking_info_queryset:
                        corr_lesson_completed_record_object = \
                            lesson_completed_record.objects.filter(lesson_booking_info_id=each_booking_info_object.id).first()
                        
                        if corr_lesson_completed_record_object is None:
                            # 這門課還沒有完課的紀錄
                            teacher_declared_start_time = ''
                            teacher_declared_end_time = ''
                            teacher_declared_time_in_minutes = ''
                            student_confirmed_deadline = ''
                            is_teacher_given_feedback = None
                            is_student_given_feedback = None
                            # 因為沒有完課，所以一定不會有評價
                        else:
                            # 這門課已完課
                            # 所以評價狀態應該只有 True 或 False 兩種狀態
                            lesson_reviews_from_students_object = \
                                lesson_reviews_from_students.objects.filter(
                                    corresponding_lesson_booking_info_id=each_booking_info_object.id
                                    ).first()  # 學生對老師的評論紀錄

                            student_reviews_from_teachers_object = \
                                student_reviews_from_teachers.objects.filter(
                                    corresponding_lesson_booking_info_id=each_booking_info_object.id
                                    ).first()  # 老師對學生的評論紀錄

                            teacher_declared_start_time = \
                                corr_lesson_completed_record_object.teacher_declared_start_time.strftime("%H:%M")
                            teacher_declared_end_time = \
                                corr_lesson_completed_record_object.teacher_declared_end_time.strftime("%H:%M")
                            teacher_declared_time_in_minutes = \
                                corr_lesson_completed_record_object.teacher_declared_time_in_minutes
                            student_confirmed_deadline = \
                                 corr_lesson_completed_record_object.student_confirmed_deadline
                            is_teacher_given_feedback = False if student_reviews_from_teachers_object is None else True
                            is_student_given_feedback = False if lesson_reviews_from_students_object is None else True

                        teacher_object = \
                            teacher_profile.objects.get(auth_id=each_booking_info_object.teacher_auth_id)
                        
                        response['data'].append(
                            {
                                'booked_date': each_booking_info_object.booking_date_and_time.split(':')[0],
                                'booked_time': each_booking_info_object.booking_date_and_time.split(':')[1][:-1].split(','),
                                # 去掉最後的 ';'
                                'booked_status': each_booking_info_object.booking_status,
                                'lesson_title': \
                                    lesson_info.objects.get(id=each_booking_info_object.lesson_id).lesson_title,
                                'teacher_auth_id': \
                                    each_booking_info_object.teacher_auth_id,
                                'teacher_nickname': teacher_object.nickname,
                                'teacher_thumbnail_path': teacher_object.thumbnail_dir,
                                'discount_price': \
                                    lesson_sales_sets.objects.get(id=each_booking_info_object.booking_set_id).sales_set,
                                'remaining_time': each_booking_info_object.remaining_minutes,
                                'lesson_booking_info_id': each_booking_info_object.id,
                                'teacher_declared_start_time': teacher_declared_start_time,
                                'teacher_declared_end_time': teacher_declared_end_time,
                                'teacher_declared_time_in_minutes': teacher_declared_time_in_minutes,
                                'student_confirmed_deadline': student_confirmed_deadline,
                                'remark': each_booking_info_object.remark, 
                                'is_teacher_given_feedback': is_teacher_given_feedback,
                                'is_student_given_feedback': is_student_given_feedback
                            }
                        )

                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None

    else:
        # 資料傳輸出現問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)
 

@require_http_methods(['POST'])
def lesson_completed_notification_from_teacher(request):
    '''
    完課後，老師應該主動向學生發起確認課程時數的要求，以便計算時數；
    這個API會連帶的建立 lesson_completed_record 資料，並且發送通知給學生(這段還沒做)。
    接收：{
        token,
        userID: 老師的auth_id
        lesson_booking_info_id: 哪一門預約的ID
        lesson_date: 上課的日期  如 2021-01-01
        start_time: 開始的時間 xx:xx  每十分鐘一跳
        end_time: 結束的時間 xx:xx  每十分鐘一跳 
        time_interval_in_minutes: 時段有多少分鐘
    }
    回傳：{
        status: “success“ / “failed“ 
        errCode: None 
        errMsg: None
        data: None
    }
    '''
    response = dict()
    teacher_auth_id = request.POST.get('userID', False)
    lesson_booking_info_id = request.POST.get('lesson_booking_info_id', False)
    lesson_date = request.POST.get('lesson_date', False)
    start_time = request.POST.get('start_time', False)
    end_time = request.POST.get('end_time', False)
    time_interval_in_minutes = request.POST.get('time_interval_in_minutes', False)


    if check_if_all_variables_are_true(teacher_auth_id, lesson_booking_info_id, 
        lesson_date, start_time, end_time, time_interval_in_minutes):
        # 資料有正確收取
        # 確認一下 teacher 、 booking_info 、 與對應的 student 存不存在
        teacher_object = teacher_profile.objects.filter(auth_id=teacher_auth_id).first()
        booking_object = lesson_booking_info.objects.filter(id=lesson_booking_info_id).first()

        if booking_object is None or teacher_object is None:
            # 沒有抓到對應的預約或是老師的紀錄
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
        elif teacher_object.auth_id != booking_object.teacher_auth_id:
            # 預約的老師 auth_id 跟前端回傳的老師 auth_id 不 match
            response['status'] = 'failed'
            response['errCode'] = '2'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
        elif booking_object.booking_status != 'confirmed':
            # 該預約狀態不為confirmed，因此老師不能完成授課
            response['status'] = 'failed'
            response['errCode'] = '3'
            response['errMsg'] = '不好意思，只有經過雙方確認的預約課程才可以進行完課動作唷，如果持續遇到這個問題請您告訴我們一聲。'
            response['data'] = None
        else:
            # 有抓到對應的預約以及老師的紀錄
            # 產生對應的 lesson_completed_record 紀錄
            _year, _month, _day = [int(_) for _ in lesson_date.split('-')]
            start_hour, start_minute = [int(_) for _ in start_time.split(':')]
            end_hour, end_minute = [int(_) for _ in end_time.split(':')]

            teacher_declared_start_time = \
                datetime(_year, _month, _day, start_hour, start_minute)
            teacher_declared_end_time = \
                datetime(_year, _month, _day, end_hour, end_minute)
            
            if not (start_minute % 10 == 0 and end_minute % 10 == 0 and 
                teacher_declared_end_time > teacher_declared_start_time):
                # 不是以每十分鐘為一個單位，或結束時間未大過起始時間
                response['status'] = 'failed'
                response['errCode'] = '4'
                response['errMsg'] = '不好意思，課程確認時間以每十分鐘為一個單位，而且結束時間要大於起始時間，如果持續遇到這個問題請您告訴我們一聲。'
                response['data'] = None
            
            else:
                # 格式都正確
                # 先確認該課程完課紀錄是否已經存在，沒有的話才建立，避免重複紀錄
                if not lesson_completed_record.objects.filter(
                    lesson_booking_info_id = booking_object.id,
                    teacher_auth_id = teacher_auth_id,
                    student_auth_id = booking_object.student_auth_id
                ).exists():
                
                    teacher_declared_time_in_minutes = \
                        int((teacher_declared_end_time - teacher_declared_start_time).seconds / 60)

                    new_added_record = lesson_completed_record.objects.create(
                        lesson_booking_info_id = booking_object.id,
                        student_remaining_minutes_of_each_purchased_lesson_set_id = \
                            booking_object.remaining_minutes,  # 對應的訂單所剩的時數
                        teacher_auth_id = teacher_auth_id,
                        student_auth_id = booking_object.student_auth_id, 
                        booking_time_in_minutes = booking_object.get_booking_time_in_minutes(),
                        # 預估上課時間時數,單位分鐘,是用預約的時間計算的
                        teacher_declared_start_time = teacher_declared_start_time,
                        teacher_declared_end_time = teacher_declared_end_time,
                        teacher_declared_time_in_minutes = teacher_declared_time_in_minutes,
                        # 老師號稱的開課時間總時數,可能課程實際時間會比原本預約時有所增減(單位是分鐘)
                        student_confirmed_deadline = \
                            date_function.today() + timedelta(days=3),
                        # 這個的作用是，假設學生遲遲不確認，我們還是要在某個時段過後撥錢給老師，
                        # 目前先預設3天? 也就是說，當在老師發送確認訊息後的3天後，假設學生還沒確認也沒申訴，
                        # 則我們將直接撥款給老師
                        # 萬一學生遲遲不確認，要由我們自動確認的話，最好也做個註記
                    )
                    new_added_record.save()
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                    response['data'] = new_added_record.id
                
                else:
                    # 已經有紀錄存在了，拒絕建立新紀錄
                    response['status'] = 'failed'
                    response['errCode'] = '4'
                    response['errMsg'] = '您已經確認完課囉，如果持續遇到這個問題請您告訴我們一聲。'
                    response['data'] = None
    else:
        # 資料傳輸出現問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)



@require_http_methods(['POST'])
def lesson_completed_confirmation_from_student(request):
    '''
    完課後老師會寄送完課通知給學生，請學生確認；
    這個API能讓學生進行完課通知的同意或是申訴(時數有爭議)。
    接收：{
        token,
        userID: 學生的auth_id
        lesson_booking_info_id: 哪一門預約的ID
        action: "agree" or "disagree"  學生的動作 
    }
    回傳：{
        status: “success“ / “failed“ 
        errCode: None 
        errMsg: None
        data: None
    }'''
    response = dict()
    student_auth_id = request.POST.get('userID', False)
    lesson_booking_info_id = request.POST.get('lesson_booking_info_id', False)
    action = request.POST.get('action', False)

    if check_if_all_variables_are_true(student_auth_id, lesson_booking_info_id, action):
        # 資料有正確收取
        # 確認一下 student 、 booking_info 存不存在
        student_object = student_profile.objects.filter(auth_id=student_auth_id).first()
        booking_object = lesson_booking_info.objects.filter(id=lesson_booking_info_id).first()

        if booking_object is None or student_object is None:
            # 沒有抓到對應的預約或是學生的紀錄
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
        elif student_object.auth_id != booking_object.student_auth_id:
            # 預約的學生 auth_id 跟前端回傳的學生 auth_id 不 match
            response['status'] = 'failed'
            response['errCode'] = '2'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
        else:
            # 看來一切正常，接下來要來更新對應的 預約 & 課程完結 兩張 TABLE 的對應資料了
            lesson_completed_object = lesson_completed_record.objects.get(
                lesson_booking_info_id = lesson_booking_info_id
            )  # 因為一定有資料，所以可以用get
            
            if action == 'agree':
                # 學生確認老師聲稱的時數無誤，先 update 預約 TABLE
                booking_object.last_changed_by = 'student'  # 因為是學生最後確認的
                booking_object.booking_status = 'finished'  # 課程完結囉~
                booking_object.save()
                # 再來 update 完結 TABLE
                lesson_completed_object.is_student_confirmed = True
                lesson_completed_object.save()
                # 之後還有時數要從remaining那邊扣掉的環節，暫時先不管  >>  現在要來處理了!

                # 先依照是不是試教，來進行開發，因為試教比較簡單，不管時數剛好、超過、或過少，都直接扣掉就是了
                if lesson_sales_sets.objects.get(id=booking_object.booking_set_id).sales_set == 'trial':
                    # 是試教
                    student_remaining_object = \
                        student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                            student_auth_id = student_auth_id,
                            teacher_auth_id = booking_object.teacher_auth_id,
                            lesson_sales_set_id = booking_object.booking_set_id).first()
                    
                    if not student_remaining_object is None:
                        # 有找到對應的 student_remaining_object ，理論上不該找不到
                        student_remaining_object.withholding_minutes -= 30
                        student_remaining_object.confirmed_consumed_minutes += 30
                        student_remaining_object.save()
                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = None
                    
                    else:
                        # 找不到對應的 student_remaining_object ，雖然不知道為甚麼會這樣
                        response['status'] = 'failed'
                        response['errCode'] = '3'
                        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                        response['data'] = None

                else:
                    # 接下來做 非試教 的部份，因為像 10:90、20:80 這種跟 no_discount 的處理方式是一樣的，
                    # 所以就傪在一起處理了
                    # 要排除 試教 購買方案，所以必須要抓出該門課所有的試教 sets 加以排除
                    # 另外也要排除 available == 0 AND withholding == 0 的購買方案們，
                    # 因為也沒有辦法從它們身上扣東西
                    
                    all_trial_set_ids_of_the_lesson = \
                        lesson_sales_sets.objects.values_list('id', flat=True).filter(
                            lesson_id = booking_object.lesson_id,
                            sales_set = 'trial')

                    student_remaining_objects = \
                        student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                            student_auth_id = student_auth_id,
                            lesson_id = booking_object.lesson_id).exclude(
                                Q(lesson_sales_set_id__in = all_trial_set_ids_of_the_lesson) |  # 排除試教方案
                                (Q(available_remaining_minutes=0) & Q(withholding_minutes=0))  # 排除兩者皆為0
                            ).order_by('created_time')  # 依照時間排序，先進先出
                    
                    # 先處理 老師宣稱的時數 == 當初預定的課堂時數
                    if lesson_completed_object.teacher_declared_time_in_minutes == lesson_completed_object.booking_time_in_minutes:
                        # 最簡單的情境，只要把對應的 remaining_object 中 對應的 withholding 移到 consumed 就好了
                        # 究竟要扣多少時數 >> lesson_completed_object.teacher_declared_time_in_minutes
                        how_many_minutes_does_it_left = lesson_completed_object.teacher_declared_time_in_minutes
                        # 還需要扣多少時間
                        
                        for each_student_remaining_object in student_remaining_objects:
                            if each_student_remaining_object.withholding_minutes >= how_many_minutes_does_it_left:
                                # 目前這個購買方案的時數>=需要扣掉的時數，所以直接扣掉就好了
                                each_student_remaining_object.withholding_minutes -= how_many_minutes_does_it_left
                                each_student_remaining_object.confirmed_consumed_minutes += how_many_minutes_does_it_left
                                each_student_remaining_object.save()
                                how_many_minutes_does_it_left = 0
                                break
                            else:
                                # 目前這個購買方案的時數不足以完全扣除需要扣除的時數
                                how_many_minutes_does_it_left -= each_student_remaining_object.withholding_minutes
                                # 先扣掉能扣掉的部份
                                # 移動到 confirmed_consumed_minutes 去
                                each_student_remaining_object.confirmed_consumed_minutes += each_student_remaining_object.withholding_minutes
                                each_student_remaining_object.withholding_minutes = 0
                                each_student_remaining_object.save()
                                # withholding_minutes歸零

                        # 迴圈跑完就自動大功告成了
                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = None

                    elif lesson_completed_object.teacher_declared_time_in_minutes > lesson_completed_object.booking_time_in_minutes:
                        # 老師宣稱的時數 != 當初預定的課堂時數
                        # 先來做超時的部份
                        # 超時的話，先扣除原先 withholding 的部份，然後再趁機從多的 available 扣除
                        # 若學生沒有多的 available 可以扣，則先儲存在 student_owing_teacher_time TABLE，留待日後處理
                        how_many_withholding_minutes_does_it_left = lesson_completed_object.booking_time_in_minutes
                        # withholding 的部份還需要扣多少時間
                        how_many_extra_minutes_does_it_left = \
                            lesson_completed_object.teacher_declared_time_in_minutes - lesson_completed_object.booking_time_in_minutes
                        # 超出的部分還需要扣多少時間

                        for each_student_remaining_object in student_remaining_objects:
                            # 先處理有預扣的部份，這一塊不受學生有沒有足夠的 available minutes 影響，所以在這裡做
                            if each_student_remaining_object.withholding_minutes >= how_many_withholding_minutes_does_it_left:
                                # 目前這個購買方案的時數>=需要扣掉的時數，所以直接扣掉就好了
                                each_student_remaining_object.withholding_minutes -= how_many_withholding_minutes_does_it_left
                                each_student_remaining_object.confirmed_consumed_minutes += how_many_withholding_minutes_does_it_left
                                each_student_remaining_object.save()
                                how_many_withholding_minutes_does_it_left = 0
                                break
                            else:
                                # 目前這個購買方案的時數不足以完全扣除需要扣除的時數
                                how_many_withholding_minutes_does_it_left -= each_student_remaining_object.withholding_minutes
                                # 先扣掉能扣掉的部份
                                # 移動到 confirmed_consumed_minutes 去
                                each_student_remaining_object.confirmed_consumed_minutes += each_student_remaining_object.withholding_minutes
                                each_student_remaining_object.withholding_minutes = 0
                                each_student_remaining_object.save()
                                # withholding_minutes歸零

                        # 再來確認該學生有沒有多餘的 available minutes 可供扣除
                        # all_available_minutes_of_this_lesson = \
                        #    student_remaining_objects.aggregate(Sum('available_remaining_minutes'))['available_remaining_minutes__sum']
                        # 好像也不用特別確認，最後有剩下的 how_many_extra_minutes_does_it_left 就代表沒扣光了

                        for each_student_remaining_object in student_remaining_objects:
                            # 再來處理扣除 available minutes 的部份
                            if each_student_remaining_object.available_remaining_minutes >= how_many_extra_minutes_does_it_left:
                                # 目前這個購買方案的時數>=需要扣掉的時數，所以直接扣掉就好了
                                each_student_remaining_object.available_remaining_minutes -= how_many_extra_minutes_does_it_left
                                each_student_remaining_object.confirmed_consumed_minutes += how_many_extra_minutes_does_it_left
                                each_student_remaining_object.save()
                                how_many_extra_minutes_does_it_left = 0
                                break
                            else:
                                # 目前這個購買方案的時數不足以完全扣除需要扣除的時數
                                how_many_extra_minutes_does_it_left -= each_student_remaining_object.available_remaining_minutes
                                # 先扣掉能扣掉的部份
                                # 移動到 confirmed_consumed_minutes 去
                                each_student_remaining_object.confirmed_consumed_minutes += each_student_remaining_object.available_remaining_minutes
                                each_student_remaining_object.available_remaining_minutes = 0
                                each_student_remaining_object.save()
                                # available_remaining_minutes

                        if how_many_extra_minutes_does_it_left:
                            # 學生的 available minutes 不足以支付多出的時數
                            # 超時的部份沒扣光，要存入 student_owing_teacher_time TABLE
                            student_owing_teacher_time.objects.create(
                                student_auth_id = student_auth_id,
                                teacher_auth_id = booking_object.teacher_auth_id,
                                lesson_id = booking_object.lesson_id,
                                lesson_booking_info_id = booking_object.id,
                                owing_minutes = how_many_extra_minutes_does_it_left
                            )
                        else:
                            # 學生的 available minutes 可以支付多出的時數，已經扣乾淨了
                            # 不用特別處理
                            pass
                            
                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = None

                    elif lesson_completed_object.teacher_declared_time_in_minutes < lesson_completed_object.booking_time_in_minutes:
                        # 現在來做萬一老師實際上課的時間比預約的時間來得短
                        # 其實算簡單，只要把 少的時間 ，從 withholding 移回去 available minutes 就好了
                        how_many_withholding_minutes_does_it_left = lesson_completed_object.teacher_declared_time_in_minutes
                        #  withholding 的部份要扣多少時間
                        shortage_minutes = \
                            lesson_completed_object.booking_time_in_minutes - lesson_completed_object.teacher_declared_time_in_minutes
                        # 短少的，要補回的時間

                        for each_student_remaining_object in student_remaining_objects:
                            # 先處理扣除的部份
                            if each_student_remaining_object.withholding_minutes >= how_many_withholding_minutes_does_it_left:
                                # 目前這個購買方案的時數>=需要扣掉的時數，所以直接扣掉就好了
                                each_student_remaining_object.withholding_minutes -= how_many_withholding_minutes_does_it_left
                                each_student_remaining_object.confirmed_consumed_minutes += how_many_withholding_minutes_does_it_left
                                each_student_remaining_object.save()
                                how_many_withholding_minutes_does_it_left = 0
                                break
                            else:
                                # 目前這個購買方案的時數不足以完全扣除需要扣除的時數
                                how_many_withholding_minutes_does_it_left -= each_student_remaining_object.withholding_minutes
                                # 先扣掉能扣掉的部份
                                # 移動到 confirmed_consumed_minutes 去
                                each_student_remaining_object.confirmed_consumed_minutes += each_student_remaining_object.withholding_minutes
                                each_student_remaining_object.withholding_minutes = 0
                                each_student_remaining_object.save()
                                # withholding_minutes歸零

                        # 接下來處理少上的時數，要補回去學生的 available minutes 部份
                        # 因為已經有事先預扣了，所以一定要從預扣補回
                        for each_student_remaining_object in student_remaining_objects:
                            # 來處理時數補回的部份
                            if each_student_remaining_object.withholding_minutes >= shortage_minutes:
                                # 目前這個購買方案的時數>=需要補回的時數，所以直接補回就好了
                                each_student_remaining_object.withholding_minutes -= shortage_minutes
                                each_student_remaining_object.available_remaining_minutes += shortage_minutes
                                each_student_remaining_object.save()
                                shortage_minutes = 0
                                break
                            else:
                                # 目前這個購買方案的時數不足以完全補回需要補回的時數
                                shortage_minutes -= each_student_remaining_object.withholding_minutes
                                # 先補回能補回的部份
                                # 移動到 available_remaining_minutes 去
                                each_student_remaining_object.available_remaining_minutes += each_student_remaining_object.withholding_minutes
                                each_student_remaining_object.withholding_minutes = 0
                                each_student_remaining_object.save()
                                # withholding_minutes歸零

                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = None

            elif action == 'disagree':
                # 學生對老師聲稱的時數有意見，先 update 預約 TABLE
                booking_object.last_changed_by = 'student'  # 因為是學生最後確認的
                booking_object.booking_status = 'quikok_dealing_for_student_disagreed'  # Quikok介入調查
                booking_object.save()
                # 再來 update 完結 TABLE
                lesson_completed_object.is_student_disagree_with_teacher_s_declared_time = True
                lesson_completed_object.save()

                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
                response['data'] = None

    else:
        # 資料傳輸出現問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)


@require_http_methods(['POST'])
def teacher_write_student_reviews(request):
    '''
    完課後老師與學生可以互評評價；
    這個API能讓老師對學生評價。
    接收：{
        token,
        userID: 老師的auth_id
        score_given: 評分 1 - 5
        remark_given: 評語
        is_student_late_for_lesson: 學生是否遲到
        is_student_frivolous_in_lesson: 學生是否不專心
        is_student_or_parents_not_friendly: 學生是否不友善
    }
    回傳：{
        status: “success“ / “failed“ 
        errCode: None 
        errMsg: None
        data: None
    }'''
    response = dict()
    teacher_auth_id = request.POST.get('userID', False)
    score_given = request.POST.get('score_given', False)
    lesson_booking_info_id = request.POST.get('lesson_booking_info_id', False)
    remark_given = request.POST.get('remark_given', False)
    is_student_late_for_lesson = request.POST.get('is_student_late_for_lesson', False)
    is_student_frivolous_in_lesson = request.POST.get('is_student_frivolous_in_lesson', False)
    is_student_or_parents_not_friendly = request.POST.get('is_student_or_parents_not_friendly', False)

    if False not in (teacher_auth_id, score_given, remark_given, lesson_booking_info_id,
        is_student_late_for_lesson, is_student_frivolous_in_lesson, is_student_or_parents_not_friendly):
        # 資料有正確收取

        lesson_booking_object = lesson_booking_info.objects.filter(id=lesson_booking_info_id).first()
        if lesson_booking_object is not None:
            # 該預約確實存在
            student_object = student_profile.objects.filter(auth_id=lesson_booking_object.student_auth_id).first()

            if (student_object is not None and lesson_booking_object.teacher_auth_id == int(teacher_auth_id)):
                # 學生存在，且該老師匹配
                if lesson_booking_object.booking_status in ('finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed'):
                
                    # 接著確認一下該門預約是否未經老師評價過
                    if student_reviews_from_teachers.objects.filter(corresponding_lesson_booking_info_id=lesson_booking_object.id).first() is None:
                        # 老師未評價過
                        # 預約課程狀態符合老師送出時段後的條件
                        # 將數值轉成符合我們的規範
                        is_student_late_for_lesson = return_none_if_the_string_is_empty(is_student_late_for_lesson)
                        is_student_frivolous_in_lesson = return_none_if_the_string_is_empty(is_student_frivolous_in_lesson)
                        is_student_or_parents_not_friendly = return_none_if_the_string_is_empty(is_student_or_parents_not_friendly)
                        remark_given = return_none_if_the_string_is_empty(remark_given)

                        # 來寫入紀錄囉
                        new_added_record = student_reviews_from_teachers.objects.create(
                            corresponding_lesson_id = lesson_booking_object.lesson_id,
                            corresponding_lesson_booking_info_id = lesson_booking_object.id,
                            corresponding_lesson_completed_record_id = \
                                lesson_completed_record.objects.get(lesson_booking_info_id=lesson_booking_object.id).id,
                            student_auth_id = student_object.auth_id,
                            teacher_auth_id = teacher_auth_id,
                            score_given = bound_number_string(score_given),
                            is_student_late_for_lesson = \
                                is_student_late_for_lesson == 'true' if is_student_late_for_lesson is not None else None,
                            is_student_frivolous_in_lesson = \
                                is_student_frivolous_in_lesson == 'true' if is_student_frivolous_in_lesson is not None else None,
                            is_student_or_parents_not_friendly = \
                                is_student_or_parents_not_friendly == 'true' if is_student_or_parents_not_friendly is not None else None,
                            remark_given = remark_given
                        )
                        new_added_record.save()

                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = new_added_record.id
                    else:
                        # 老師已經有評價過這門預約了
                        # 未來可以做成雙方可以在評價下方留言，讓外界也可以知道評價的原因與反駁
                        response['status'] = 'failed'
                        response['errCode'] = '4'
                        response['errMsg'] = '謝謝您，您已經評價過囉Y(^___^)Y'
                        response['data'] = student_reviews_from_teachers.objects.filter(corresponding_lesson_booking_info_id=lesson_booking_object.id).first().id
                else:
                    # 課程狀況不符合評價的前提
                    response['status'] = 'failed'
                    response['errCode'] = '2'
                    response['errMsg'] = '不好意思，老師必須先進行完課確認，雙方才能夠進行評價唷。'
                    response['data'] = lesson_booking_object.booking_status
            else:
                # 學生不存在，或老師不匹配
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                response['data'] = (student_object, lesson_booking_object.teacher_auth_id)

        else:
            # 沒有這樣子的一筆預約
            response['status'] = 'failed'
            response['errCode'] = '3'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = lesson_booking_object

    else:
        # 資料傳輸出現問題
        # print(f'is_student_late_for_lesson {is_student_late_for_lesson} is_student_frivolous_in_lesson {is_student_frivolous_in_lesson} is_student_or_parents_not_friendly {is_student_or_parents_not_friendly}')
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)


@require_http_methods(['POST'])
def student_write_teacher_reviews(request):
    '''
    完課後老師與學生可以互評評價；
    這個API能讓學生對老師評價。
    接收：{
        token,
        userID: 學生的auth_id
        score_given: 評分 1 - 5
        remark_given: 評語
        is_teacher_late_for_lesson: 老師是否遲到
        is_teacher_frivolous_in_lesson: 老師是否不專心
        is_teacher_incapable: 老師是否不勝任這門課、教太廢
    }
    回傳：{
        status: “success“ / “failed“ 
        errCode: None 
        errMsg: None
        data: None
    }'''
    response = dict()
    student_auth_id = request.POST.get('userID', False)
    score_given = request.POST.get('score_given', False)
    lesson_booking_info_id = request.POST.get('lesson_booking_info_id', False)
    remark_given = request.POST.get('remark_given', False)
    is_teacher_late_for_lesson = request.POST.get('is_teacher_late_for_lesson', False)
    is_teacher_frivolous_in_lesson = request.POST.get('is_teacher_frivolous_in_lesson', False)
    is_teacher_incapable = request.POST.get('is_teacher_incapable', False)

    if False not in (student_auth_id, score_given, remark_given, lesson_booking_info_id,
        is_teacher_late_for_lesson, is_teacher_frivolous_in_lesson, is_teacher_incapable):
        # 資料有正確收取

        lesson_booking_object = lesson_booking_info.objects.filter(id=lesson_booking_info_id).first()
        if lesson_booking_object is not None:
            # 該預約確實存在
            teacher_object = teacher_profile.objects.filter(auth_id=lesson_booking_object.teacher_auth_id).first()

            if (teacher_object is not None and lesson_booking_object.student_auth_id == int(student_auth_id)):
                # 老師存在，且該學生匹配
                if lesson_booking_object.booking_status in ('finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed'):
                
                    # 接著確認一下該門預約是否未經學生評價過
                    if not lesson_reviews_from_students.objects.filter(corresponding_lesson_booking_info_id=lesson_booking_object.id).exists():
                        # 學生未評價過
                        # 預約課程狀態符合老師送出時段後的條件
                        # 將數值轉成符合我們的規範
                        is_teacher_late_for_lesson = return_none_if_the_string_is_empty(is_teacher_late_for_lesson)
                        is_teacher_frivolous_in_lesson = return_none_if_the_string_is_empty(is_teacher_frivolous_in_lesson)
                        is_teacher_incapable = return_none_if_the_string_is_empty(is_teacher_incapable)
                        remark_given = return_none_if_the_string_is_empty(remark_given)

                        # 來寫入紀錄囉
                        new_added_record = lesson_reviews_from_students.objects.create(
                            corresponding_lesson_id = lesson_booking_object.lesson_id,
                            corresponding_lesson_booking_info_id = lesson_booking_object.id,
                            corresponding_lesson_completed_record_id = \
                                lesson_completed_record.objects.get(lesson_booking_info_id=lesson_booking_object.id).id,
                            student_auth_id = student_auth_id,
                            teacher_auth_id = teacher_object.auth_id,
                            score_given = bound_number_string(score_given),
                            is_teacher_late_for_lesson = \
                                is_teacher_late_for_lesson == 'true' if is_teacher_late_for_lesson is not None else None,
                            is_teacher_frivolous_in_lesson = \
                                is_teacher_frivolous_in_lesson == 'true' if is_teacher_frivolous_in_lesson is not None else None,
                            is_teacher_incapable = \
                                is_teacher_incapable == 'true' if is_teacher_incapable is not None else None,
                            remark_given = remark_given
                        )
                        new_added_record.save()

                        response['status'] = 'success'
                        response['errCode'] = None
                        response['errMsg'] = None
                        response['data'] = new_added_record.id
                    else:
                        # 學生已經有評價過這門預約了
                        # 未來可以做成雙方可以在評價下方留言，讓外界也可以知道評價的原因與反駁
                        response['status'] = 'failed'
                        response['errCode'] = '4'
                        response['errMsg'] = '謝謝您，您已經評價過囉Y(^___^)Y'
                        response['data'] = lesson_reviews_from_students.objects.filter(corresponding_lesson_booking_info_id=lesson_booking_object.id).first().id
                else:
                    # 課程狀況不符合評價的前提
                    response['status'] = 'failed'
                    response['errCode'] = '2'
                    response['errMsg'] = '不好意思，老師必須先進行完課確認，雙方才能夠進行評價唷。'
                    response['data'] = lesson_booking_object.booking_status
            else:
                # 學生不存在，或老師不匹配
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                response['data'] = (teacher_object, lesson_booking_object.student_auth_id)

        else:
            # 沒有這樣子的一筆預約
            response['status'] = 'failed'
            response['errCode'] = '3'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = lesson_booking_object

    else:
        # 資料傳輸出現問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)


@require_http_methods(['POST'])
def read_reviews_of_certain_lessons(request):
    '''
    讓師/生雙方可以看見彼此在某堂課上對彼此的評價
    接收：{
        lesson_booking_info_id: 哪一門預約的ID
        userID: 用戶的auth_id,  // 用來確認這個user是不是有權力看這個評論
        type: "student" or "teacher"
    }
    回傳：{
        status: “success“ / “failed“ 
        errCode: None 
        errMsg: None
        data: {
            // 學生對老師
            score_given_to_teacher: from 1 to 5
            remark_given_to_teacher: 評語
            is_teacher_late_for_lesson: Boolean,
            is_teacher_frivolous_in_lesson: Boolean,
            is_teacher_incapabale: Boolean,
            // 老師對學生
            score_given_to_student: from 1 to 5
            remark_given_to_student: 評語
            is_student_late_for_lesson: Boolean,
            is_student_frivolous_in_lesson: Boolean,
            is_student_or_parents_not_friendly: Boolean,
        }
    }'''
    response = dict()
    user_auth_id = request.POST.get('userID', False)
    lesson_booking_info_id = request.POST.get('lesson_booking_info_id', False)
    user_type = request.POST.get('type', False)

    if check_if_all_variables_are_true(user_auth_id, lesson_booking_info_id, user_type):
        # 資料有正確收取
        # 接著確認有沒有此門預約課程
        lesson_booking_object = lesson_booking_info.objects.filter(id=lesson_booking_info_id).first()
        if lesson_booking_object is not None:
            # 此門預約確實存在
            # 接著確認此用戶是否存在於該預約的師生雙方中
            if int(user_auth_id) in (lesson_booking_object.student_auth_id, lesson_booking_object.teacher_auth_id):
                # 因為一次要回傳雙方的評價資訊，故不需要特別區分老師或是學生來做處理
                # 確認該門課已經進入至少其中的階段之一
                if lesson_booking_object.booking_status in ('finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed'):
                    # 拿學生留的評價
                    review_left_by_student = \
                        lesson_reviews_from_students.objects.filter(
                            corresponding_lesson_booking_info_id=lesson_booking_object.id).first()

                    # 拿老師留的評價
                    review_left_by_teacher = \
                        student_reviews_from_teachers.objects.filter(
                            corresponding_lesson_booking_info_id=lesson_booking_object.id).first()

                    if review_left_by_student is None and review_left_by_teacher is None:
                        # 學生與老師都沒有留下評論
                        response['data'] = {
                                    'score_given_to_teacher': -1,
                                    'remark_given_to_teacher': '',
                                    'is_teacher_late_for_lesson': None,
                                    'is_teacher_frivolous_in_lesson': None,
                                    'is_teacher_incapable': None,
                                    'score_given_to_student': -1,
                                    'remark_given_to_student': '',
                                    'is_student_late_for_lesson': None,
                                    'is_student_frivolous_in_lesson': None,
                                    'is_student_or_parents_not_friendly': None
                                }
                    elif review_left_by_student is not None and review_left_by_teacher is None:
                        # 學生有留評論，老師沒有
                        response['data'] = {
                                    'score_given_to_teacher': review_left_by_student.score_given,
                                    'remark_given_to_teacher': review_left_by_student.remark_given,
                                    'is_teacher_late_for_lesson': review_left_by_student.is_teacher_late_for_lesson,
                                    'is_teacher_frivolous_in_lesson': review_left_by_student.is_teacher_frivolous_in_lesson,
                                    'is_teacher_incapable': review_left_by_student.is_teacher_incapable,
                                    'score_given_to_student': -1,
                                    'remark_given_to_student': '',
                                    'is_student_late_for_lesson': None,
                                    'is_student_frivolous_in_lesson': None,
                                    'is_student_or_parents_not_friendly': None
                                }
                    elif review_left_by_student is None and review_left_by_teacher is not None:
                        # 老師有留評論，學生沒有
                        response['data'] = {
                                    'score_given_to_teacher': -1,
                                    'remark_given_to_teacher': '',
                                    'is_teacher_late_for_lesson': None,
                                    'is_teacher_frivolous_in_lesson': None,
                                    'is_teacher_incapable': None,
                                    'score_given_to_student': review_left_by_teacher.score_given,
                                    'remark_given_to_student': review_left_by_teacher.remark_given,
                                    'is_student_late_for_lesson': review_left_by_teacher.is_student_late_for_lesson,
                                    'is_student_frivolous_in_lesson': review_left_by_teacher.is_student_frivolous_in_lesson,
                                    'is_student_or_parents_not_friendly': review_left_by_teacher.is_student_or_parents_not_friendly
                                }
                    else:
                        # 雙方都有留下評論
                        response['data'] = {
                                    'score_given_to_teacher': review_left_by_student.score_given,
                                    'remark_given_to_teacher': review_left_by_student.remark_given,
                                    'is_teacher_late_for_lesson': review_left_by_student.is_teacher_late_for_lesson,
                                    'is_teacher_frivolous_in_lesson': review_left_by_student.is_teacher_frivolous_in_lesson,
                                    'is_teacher_incapable': review_left_by_student.is_teacher_incapable,
                                    'score_given_to_student': review_left_by_teacher.score_given,
                                    'remark_given_to_student': review_left_by_teacher.remark_given,
                                    'is_student_late_for_lesson': review_left_by_teacher.is_student_late_for_lesson,
                                    'is_student_frivolous_in_lesson': review_left_by_teacher.is_student_frivolous_in_lesson,
                                    'is_student_or_parents_not_friendly': review_left_by_teacher.is_student_or_parents_not_friendly
                                }
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None

            else:
                # 此用戶並不是授課雙方之一
                response['status'] = 'failed'
                response['errCode'] = '2'
                response['errMsg'] = '不好意思，只有上課雙方才能閱讀特定課程的評價唷> <'
                response['data'] = None
        else:
            # 此門預約不存在
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
                   
    else:
        # 資料傳輸出現問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)



'''
if user_type == 'teacher':
# 先做用戶是老師的處理
teacher_object = teacher_profile.objects.filter(auth_id=user_auth_id).first()
if teacher_object is not None:
    # 用戶存在
    # 確認該門課已經進入至少其中的階段之一
    if lesson_booking_object.booking_status in ('finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed'):
        review_left_by_student = \
            lesson_reviews_from_students.objects.filter(
                corresponding_lesson_booking_info_id=lesson_booking_object.id).first()
        if review_left_by_student is None:
            # 學生尚未留下任何評論
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = ''
        else:
            # 學生有留下評論
            response['data'] = {
                'score_given_to_teacher': review_left_by_student.score_given,
                'remark_given_to_teacher': review_left_by_student.remark_given,
                'is_teacher_late_for_lesson': review_left_by_student.is_teacher_late_for_lesson,
                'is_teacher_frivolous_in_lesson': review_left_by_student.is_teacher_frivolous_in_lesson,
                'is_teacher_incapable': review_left_by_student.is_teacher_incapable
            }
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
else:
    # 老師用戶不存在
    response['status'] = 'failed'
    response['errCode'] = '4'
    response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
    response['data'] = None

else:
# 用戶是學生
student_object = student_profile.objects.filter(auth_id=user_auth_id).first()
if student_object is not None:
    # 用戶存在
    # 確認該門課已經進入至少其中的階段之一
    if lesson_booking_object.booking_status in ('finished', 'student_not_yet_confirmed', 'quikok_dealing_for_student_disagreed'):
        review_left_by_teacher = \
            student_reviews_from_teachers.objects.filter(
                corresponding_lesson_booking_info_id=lesson_booking_object.id).first()
        if review_left_by_teacher is None:
            # 老師尚未留下任何評論
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = ''
        else:
            # 老師有留下評論
            response['data'] = {
                'score_given_to_student': review_left_by_teacher.score_given,
                'remark_given_to_student': review_left_by_teacher.remark_given,
                'is_student_late_for_lesson': review_left_by_teacher.is_student_late_for_lesson,
                'is_student_frivolous_in_lesson': review_left_by_teacher.is_student_frivolous_in_lesson,
                'is_student_or_parents_not_friendly': review_left_by_teacher.is_student_or_parents_not_friendly
            }
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
else:
    # 用戶不存在
    response['status'] = 'failed'
    response['errCode'] = '3'
    response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
    response['data'] = None
'''