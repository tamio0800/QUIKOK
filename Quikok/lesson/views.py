from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import os
from django.contrib.auth.models import User
from account.models import student_profile, teacher_profile, specific_available_time, general_available_time
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
from account.models import teacher_profile, favorite_lessons
from lesson.models import lesson_info, lesson_reviews, lesson_card
from lesson.lesson_tools import *
from django.contrib.auth.decorators import login_required
from account.model_tools import *
from django.db.models import Q

def check_if_all_variables_are_true(*args):
    print(args)
    for each_arg in args:
        if each_arg == False:
            return False
    return True

def sort_dictionaries_in_a_list_by_specific_key(specific_key, followed_by_values_in_list, the_list):
    _new_mapping_dict = dict()
    for each_dict in the_list:
        _new_mapping_dict[
            each_dict[specific_key]
        ] = each_dict
    _data = list()
    for each_value in followed_by_values_in_list:
        _data.append(_new_mapping_dict[each_value])
    return _data
    



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
                if not len(value_time) == 0:
                    # 如果沒有空閒時間就可以直接跳過了
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
    keywords, only_show_ones_favorites, only_show_lessons_by_this_teacher_s_auth_id,
    filtered_by, ordered_by):
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
            print(len(_data))
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
    print('action', action)
    print('teacher_auth_id', teacher_auth_id)
    print('lesson_id', lesson_id)

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
    # http://127.0.0.1:8000/api/lesson/returnLessonDetailsForTeacherWhoCreatedIt/?action=5&userID=2&lessonID=1
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
    lesson_id = request.POST.get('lessonID', False) # 新增沒有,修改才有
    # print(request.POST.get('background_picture_path', False))
    the_leeson_manager = lesson_manager()
    if not check_if_all_variables_are_true(action, teacher_auth_id):
        # 萬一有變數沒有傳到後端來的話...
        response['status'] = 'failed'
        response['errCode'] = 0
        response['errMsg'] = 'Received Arguments Failed.'
        return JsonResponse(response)
    if action == 'createLesson':
        response['status'], response['errCode'], response['errMsg']= \
            the_leeson_manager.setup_a_lesson(
                teacher_auth_id, request, None, action)
        return JsonResponse(response)
    elif action == 'editLesson':
        response['status'], response['errCode'], response['errMsg']= \
            the_leeson_manager.setup_a_lesson(
                teacher_auth_id, request, lesson_id, action)
        return JsonResponse(response)
    else:
        response['status'] = 'failed'
        response['errCode'] = 1
        response['errMsg'] = 'Unknown Action.'
        return JsonResponse(response)


@require_http_methods(['POST'])
def set_lesson_s_status(request):
    response = dict()
    action = request.POST.get('selling_status', False)
    teacher_auth_id = request.POST.get('userID', False)
    lesson_id = request.POST.get('lessonID', False) 
    print(action, teacher_auth_id, lesson_id)

    if not check_if_all_variables_are_true(action, teacher_auth_id, lesson_id):
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed.'
        return JsonResponse(response)
    
    vaildated_lesson_object = \
        lesson_info.objects.filter(teacher__auth_id=teacher_auth_id).filter(id=lesson_id).first()
    if vaildated_lesson_object is None:
        response['status'] = 'failed'
        response['errCode'] = '1'
        response['errMsg'] = 'Unmatched Lesson Id And Teacher Id.'
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
            response['errMsg'] = 'Unknown Action.'
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
                response['errMsg'] = 'Found no lesson.'
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
                    print(response)
                else:
                    response['status'] = 'failed'
                    response['errCode'] = '1'
                    response['errMsg'] = 'query failed: false in required field'
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
                    response['errMsg'] = 'update failed:cannot find this lesson'
            
            else:            # 資料傳輸有問題
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = 'wrong data: false in required field'        


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
                    print('課程自訂背景圖: ', background.name)
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
                response['errMsg'] = 'wrong data: false in required field'
        else:
            # action不等於任何值
            response['status'] = 'failed'
            response['errCode'] = '2'
            response['errMsg'] = 'what is action?'
    print(response)
    return JsonResponse(response)    

@require_http_methods(['POST'])
def before_signing_up_create_or_edit_a_lesson(request):
    response = dict()
    dummy_user_id = request.POST.get('dummy_user_id', False)
    
    if dummy_user_id != False:
        response['status'] = 'success'
        response['errCode'] = None
        response['errMsg'] = None
    else:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Non dummy_user_id'
    
    return JsonResponse(response)