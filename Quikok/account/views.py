from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password  # 這一行用來加密密碼的
from .model_tools import user_db_manager, teacher_manager, student_manager, auth_manager_for_password
from django.contrib.auth.models import User
from account.models import user_token, student_profile, teacher_profile, specific_available_time, general_available_time, feedback
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage
from lesson.models import lesson_info_for_users_not_signed_up, lesson_info
from datetime import date as date_function
import pandas as pd
from chatroom.models import chatroom_info_Mr_Q2user
from chatroom.chat_tools import chat_room_manager
from lesson.lesson_tools import *
import os
from .auth_tools import auth_check_manager
# FOR API
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
import json
from django.middleware.csrf import get_token
from datetime import datetime, timedelta
import shutil

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

def is_num(target):
    try:
        int(target)
        if int(target) == float(target):
            return True
        else:
            return False
    except:
        return False

def clean_files(folder_path, key_words):
    for each_file in os.listdir(folder_path):
        if key_words in each_file:
            os.unlink(os.path.join(folder_path, each_file))



def date_string_2_dateformat(target_string):
    if not target_string == False:
        try:
            # 將前端的 2000-01-01格式改為20000101
            nodash_str = target_string.replace('-','')
            if len(nodash_str) == 8 :
                _year, _month, _day = int(nodash_str[:4]), int(nodash_str[4:6]), int(nodash_str[-2:])
                return date_function(_year, _month, _day)
            else:
                return False
        except Exception as e:
            print(e)
            return False
    else:
        return False


## 0916改成api的版本,之前的另存成views_old, 之後依據該檔把已設計好的功能寫過來
##### 學生區 #####
@require_http_methods(['POST'])
def create_a_student_user(request):
    response = {}
    username = request.POST.get('regEmail', False)
    print('收到學生註冊:'+ username)
    # 此處的password已經經過前端加密，故無需再加密
    password = request.POST.get('regPwd', False)
    name = request.POST.get('regName', False)
    nickname = request.POST.get('regNickname', False)
    if not nickname:
        nickname = name
    birth_date = date_string_2_dateformat(request.POST.get('regBirth', False))
    is_male = request.POST.get('regGender', None) # is_male boolean
    # intro , 註冊時不需要填寫
    role = request.POST.get('regRole', False)
    #def request_get(something):
    #    if something is None:
    #        return None
    #    else:
    #        return something
    mobile = request.POST.get('regMobile', False)
    update_someone_by_email = request.POST.get('regNotifiemail', False)

    print('接收資料')
    print('學生名稱:',username, password, name, '生日:',birth_date, '角色:',role,'手機:', mobile,':信箱', update_someone_by_email,is_male)
    if False not in [username, password, name, birth_date, role, mobile, 
    update_someone_by_email] and is_male is not None:
        print('接收資料內容正常')
        # 先檢查有沒有這個username存在，存在的話會return None給obj
        obj = student_profile.objects.filter(username=username).first()
        auth_obj = User.objects.filter(username=username).first()
        # 下面這個條件式>> 皆非(a為空 或是 b為空) >> a跟b都不能為空
        if int(is_male) == 0:
            is_male = False
        else:
            is_male = True
        if obj is None and auth_obj is None:
            ### 長出每個學生相對應資料夾 目前要長的有:放大頭照的資料夾
            # 將來可能會有成績單或考卷等資料夾
            #user_folder = username #.replace('@', 'at')
            # If folder_a was not created, 
            # os.mkdir(os.path.join('folder_a', 'folder_b')) will result in an error!
            # and if folder_a was empty, GIT will ignore this folder and remove it from tracked files,
            # which may cause the error above.
            if not os.path.isdir('user_upload/students'):
                os.mkdir(os.path.join('user_upload/students'))

            if os.path.isdir(os.path.join('user_upload/students', username)):
                # 如果已經有了這個資料夾，就刪除裡面所有項目並且重建
                shutil.rmtree(os.path.join('user_upload/students', username))
                print('User Folder Already Existed >> Rebuild It.')
            os.mkdir(os.path.join('user_upload/students', username))
            os.mkdir(os.path.join('user_upload/students/'+ username, 'info_folder'))
            # 存到 user_upload 該使用者的資料夾

            #大頭照
            print('學生個人資料夾建立')
           
            # 如果沒東西 會是空的  user_upload 看前端取甚麼名字 
            each_file = request.FILES.get("upload_snapshot")
            if each_file :
                print('收到學生大頭照: ', each_file.name)
                folder_where_are_uploaded_files_be ='user_upload/students/' + username
                fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
                file_exten = each_file.name.split('.')[-1]
                fs.save('thumbnail'+'.'+ file_exten , each_file) # 檔名統一改成thumbnail開頭
                thumbnail_dir = '/user_upload/students/' + username + '/' + 'thumbnail'+'.'+ file_exten
            else:
                thumbnail_dir = ''
            #存入auth
            user_created_object = \
                User.objects.create(
                    username = username,
                    password = password,
                    is_superuser = 0,
                    first_name = '',
                    last_name = '',
                    email = '',
                    is_staff = 0,
                    is_active = 1,
                )
            # 用create()的寫法是為了知道這個user在auth裡面的id為何
            user_created_object.save()
            print('auth建立')
            print('建立新學生資料')
            new_student = student_profile.objects.create(
                auth_id = user_created_object.id,
                username = username,
                password = password,
                balance = 0,
                withholding_balance = 0,
                name = name,
                nickname = nickname,
                birth_date = birth_date,
                is_male = is_male,
                intro = '',
                role = role,
                mobile = mobile,
                user_folder = 'user_upload/'+ username,
                info_folder = 'user_upload/'+ username+ '/info_folder',
                thumbnail_dir = thumbnail_dir ,
                update_someone_by_email = update_someone_by_email
            )
            print('student_profile建立')
            
            # 建立學生與system的聊天室
            chat_tool = chat_room_manager()
            chat_tool.create_system2user_chatroom(userID=new_student.auth_id, user_type = 'student')
            print('建立學生與Mr.Q 聊天室')
            # 建立group, 現在學生都是測試:4
            user_created_object.groups.add(4)
            # 回前端
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            #response['data'] = None

        else:
            if obj is not None:
                print('此帳號已註冊過學生類別!')
            elif auth_obj is not None:
                print('此帳號已註冊到全站資料中!')
            response['status'] = 'failed'
            response['errCode'] = '0'
            response['errMsg'] = 'username taken' # 使用者已註冊
    else:
        # 資料傳輸有問題
        response['status'] = 'failed'
        response['errCode'] = '1'
        response['errMsg'] = 'wrong data'
    
    return JsonResponse(response)


@require_http_methods(['GET'])
def return_student_profile_for_oneself_viewing(request):
    response = dict()
    student_auth_id = request.GET.get('userID', False)
    the_student_manager = student_manager()
    if student_auth_id == False:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed.'
        response['data'] = None
        return JsonResponse(response)
    else:    
        response['status'], response['errCode'], response['errMsg'], response['data'] = \
            the_student_manager.return_student_profile_for_oneself_viewing(student_auth_id)
        return JsonResponse(response)


@require_http_methods(['POST'])
def edit_student_profile(request):
    response = dict()
    pass_data_to_model_tools = dict()

    for key, value in request.POST.items():
        pass_data_to_model_tools[key] = request.POST.get(key,False)
    # 要處理的資料
    #recevived_data_name = ['token','userID','mobile','nickname','update_someone_by_email',
    # 'intro']
    # 上傳檔案的種類:大頭照
    userupload_file_kind = ['upload_snapshot']
    for each_kind_of_upload_file in userupload_file_kind:
        file_list = request.FILES.getlist(each_kind_of_upload_file)
        #print('上傳種類')
        #print(file_list)
        if len(file_list) > 0 :
            pass_data_to_model_tools[each_kind_of_upload_file] = request.FILES.getlist(each_kind_of_upload_file)
            #print(each_kind_of_upload_file+'傳東西')
        else:
            pass_data_to_model_tools[each_kind_of_upload_file] = False
            #print(each_kind_of_upload_file + '沒東西')
    the_student_manager = student_manager()

    response['status'], response['errCode'], response['errMsg'], response['data'] =\
    the_student_manager.update_student_profile(**pass_data_to_model_tools)
    print('passing data' + str(pass_data_to_model_tools))
    print(response)
    return JsonResponse(response)

##### 老師區 #####
# 老師編輯個人資料
@require_http_methods(['POST'])
def edit_teacher_profile(request):
    response = dict()
    pass_data_to_model_tools = dict()
    for key, value in request.POST.items():
        pass_data_to_model_tools[key] = request.POST.get(key,False)
        print('this is a pair of key, value:' + key + value)
    the_teacher_manager = teacher_manager()
    print(pass_data_to_model_tools)
    # 上傳檔案的種類:大頭照、證書
    userupload_file_kind = ["upload_snapshot", "upload_cer"]
    #each_file = request.FILES.get("upload_snapshot")
    #    if each_file :
    for each_kind_of_upload_file in userupload_file_kind:
        file_list = request.FILES.getlist(each_kind_of_upload_file)
        if len(file_list) > 0 :
            pass_data_to_model_tools[each_kind_of_upload_file] = request.FILES.getlist(each_kind_of_upload_file)
            #print(each_kind_of_upload_file+'傳東西')
        else:
            pass_data_to_model_tools[each_kind_of_upload_file] = False
            #print(each_kind_of_upload_file + '沒東西')

    response['status'], response['errCode'], response['errMsg'], response['data'] =\
    the_teacher_manager.edit_teacher_profile_tool(**pass_data_to_model_tools)
 
    return JsonResponse(response)


def check_if_has_dummy_teacher_id_variable(create_a_teacher_view_func):

    class lesson_ETL_manager:
        # 將 課程從暫存資料庫轉移到正式的資料庫
        def __init__(self):
            self.excluded_columns = ['id', 'created_time', 'dummy_teacher_id']
            self.arguments_dict = dict()

        def query_temp_lesson_info_from_db(self, dummy_teacher_id, teacher_auth_id):
            # 根據給定的 dummy_teacher_id 查值, 並存在 self.arguments_dict 中
            self.dummy_teacher_id = dummy_teacher_id
            self.teacher_auth_id = teacher_auth_id
            temp_lesson_info_values = \
                lesson_info_for_users_not_signed_up.objects.filter(dummy_teacher_id=dummy_teacher_id).values().first()

            for each_key, each_value in temp_lesson_info_values.items():
                if each_key not in self.excluded_columns:
                    self.arguments_dict[each_key] = each_value
            
            self.arguments_dict['teacher'] = teacher_profile.objects.filter(auth_id=teacher_auth_id).first()
            # self.arguments_dict['teacher_id'] = self.arguments_dict['teacher'].id
            self.arguments_dict['discount_price'] = ''
            self.arguments_dict['lesson_avg_score'] = 0.0
            self.arguments_dict['lesson_reviewed_times'] = 0
            self.arguments_dict['selling_status'] = 'selling'

        def ETL_to_lesson_info(self):
            
            # ================創建正式課程================
            new_added_lesson_info = \
                lesson_info.objects.create(
                    **self.arguments_dict
                )
            # 這裏還不能儲存，原因是需要等到課程建立後我們才能用課程的id 賦名予課程資訊的folder
            #new_added_lesson_info.save()   
            # ================創建正式課程================
          
            # ================處理用戶自訂的上傳圖片================
            lessons_folder_path = \
                    'user_upload/teachers/' + self.arguments_dict['teacher'].username + '/lessons/' + str(new_added_lesson_info.id)
            if not os.path.isdir(lessons_folder_path):
                os.mkdir(lessons_folder_path)
            if self.arguments_dict['background_picture_path'] != '':
                # 代表user有傳入自定義的背景圖片，我們要幫他移動過去到正確的地方
                os.rename(
                    self.arguments_dict['background_picture_path'][1:],
                    lessons_folder_path + '/' + self.arguments_dict['background_picture_path'].split('/')[-1]
                )
                # 接著將參數改正
                self.arguments_dict['background_picture_path'] = \
                    '/' + lessons_folder_path + '/' + self.arguments_dict['background_picture_path'].split('/')[-1]
            # ================處理用戶自訂的上傳圖片================

            # ================更改課程資訊的背景圖片位置並儲存================
            new_added_lesson_info.background_picture_path = \
                self.arguments_dict['background_picture_path']
            new_added_lesson_info.save()
            # ================更改課程資訊的背景圖片位置並儲存================

            # ================創建課程小卡================
            the_lesson_card_manager = lesson_card_manager()
            the_lesson_card_manager.setup_a_lesson_card(
                corresponding_lesson_id = new_added_lesson_info.id,
                teacher_auth_id = self.teacher_auth_id
                )
            # ================創建課程小卡================

            lesson_info_for_users_not_signed_up.objects.filter(dummy_teacher_id=self.dummy_teacher_id).delete()
            # 刪除暫存區的資料
            return new_added_lesson_info.id

    def wrapper(request, *args, **kwargs):
        if request.POST.get('dummy_teacher_id', False) not in [False, '', 'False']:
            # 代表有找到 dummy_teacher_id 這個變數，所以我們要幫這名老師註冊完後進行上架
            # 因為要上架課程，所以我們必須知道他的auth_id，不能直接return函式的運算結果
            dummy_teacher_id = request.POST.get('dummy_teacher_id', False)
            response = create_a_teacher_view_func(request, *args, **kwargs)
            this_teacher_user_auth_id = json.loads(str(response.content, 'utf8'))['data']
            # 先取得剛註冊好的老師的auth_id，以備上架使用
            print('this_teacher_user_auth_id', this_teacher_user_auth_id, type(this_teacher_user_auth_id))
            # 接著把上架寫在這裡吧
            the_lesson_ETL_manager = lesson_ETL_manager()
            the_lesson_ETL_manager.query_temp_lesson_info_from_db(
                dummy_teacher_id=dummy_teacher_id,
                teacher_auth_id=this_teacher_user_auth_id
            )
            new_added_lesson_id = the_lesson_ETL_manager.ETL_to_lesson_info()
            print('new_added_lesson_id', new_added_lesson_id)
            return response
        else:
            # 代表沒找到 dummy_teacher_id 這個變數，直接執行創立老師用戶即可。
            return create_a_teacher_view_func(request, *args, **kwargs)
    
    return wrapper


@require_http_methods(['POST'])
@check_if_has_dummy_teacher_id_variable
def create_a_teacher_user(request):    
    response = {}
    username = request.POST.get('regEmail', False) # 當前端值有錯誤傳 null 就會是false 
    password = request.POST.get('regPwd', False)
    # origin >> balance = request.POST.get('balance', False)
    # origin >> withholding_balance = request.POST.get('withholding_balance', False)
    # 不用寫上面那兩個，因為一開始老師註冊的時候不會有這兩個資訊，我們寫入db時主動帶入0就好了
    name = request.POST.get('regName', False)
    nickname = request.POST.get('regNickname', False)
    if not nickname:
        nickname = name
    birth_date = date_string_2_dateformat(request.POST.get('regBirth', False))
    is_male = request.POST.get('regGender', None)
    if int(is_male) == 0:
        is_male = False
    else:
        is_male = True
    # origin >> intro = request.POST.get('intro', None)
    # tata >> 要改成False，因為若回傳None時使用len()會出錯
    intro = request.POST.get('intro', False)
    # 而字串可以使用len()函式，len(空字串)會回傳False，len(非空字串時)也可以是True的意思。
    # 另外下方寫法本來是str(intro)，其實不需要str()，因為前端傳來的就是string格式了;
    # 另外，讓前端去判斷「自我介紹至少填入5個字」會簡單很多，所以我們讓前端去做。
    # origin >> if not len(str(intro)) < 5 : # 自我介紹至少填入5個字
    # origin >>     intro = False
    # origin >> else:
    # origin >>     intro = True
    mobile = request.POST.get('regMobile', False)
    # origin >> user_folder = request.POST.get('user_folder', False)
    # 我們自己建的，不需要前端/user給我們資料

    # origin >> info_folder = request.POST.get('info_folder', False) # 資料夾路徑，存放個人檔案（暫不使用）
    # 我們自己建的，不需要前端/user給我們資料
    #info_folder = 'some/where/we/create/by/username'
    tutor_experience = request.POST.get('tutor_experience', False)
    subject_type = request.POST.get('subject_type', False)
    education_1 = request.POST.get('education_1', False) # 沒填的話前端傳空的過來
    education_2 = request.POST.get('education_2', False)
    education_3 = request.POST.get('education_3', False)
    # origin >> cert_unapproved = request.POST.get('cert_unapproved', False)
    # origin >> cert_approved = request.POST.get('cert_approved', False)
    # origin >> id_approved = request.POST.get('id_approved', False)
    # origin >> education_approved = request.POST.get('education_approved', False)
    # origin >> work_approved = request.POST.get('work_approved', False)
    # origin >> other_approved = request.POST.get('other_approved', False)  #其他類別的認證勳章
    # 以上的原因也一樣，因為這些性質是資料夾路徑(我們自己建的)，不需要前端/user給我們資料
    # 但我們可能需要一些變數，來跟前端拿取user上傳的資料，不過我們頁面只有一個上傳欄位，
    # 或許我們先經過人工審核後再決定要分別放到哪一個資料夾去？
    # 另外，我們也要跟GARY確認一下user註冊時的上傳資料會用什麼形式讓後端接收，
    # 目前這個api裡面還沒有這個機制。
    # 0916 為了做到上面這部分，使用者上傳的檔案前端統一給我們　userupload_files
    # 再用 files system從userupload_files 儲存到相對的位置
    company = request.POST.get('company', False) # 包含職位 occupation資訊
    special_exp = request.POST.get('special_exp', False)
    # 一般開課時間

    # print(is_male)
    # # http://127.0.0.1:8000/api/create_teacher/?username=testUser3&password=1111&name=tata3&birth_date=19901225&is_male=1
    user_folder = username #.replace('@', 'at')
    print('收到老師註冊資料')
    if False not in [
        username, password, name, intro, subject_type, mobile,
        tutor_experience, subject_type
    ] and is_male is not None:
        print('判斷收到老師資料是正常的')
        # 先檢查有沒有這個username存在，存在的話會return None給obj
        obj = teacher_profile.objects.filter(username=username).first()
        auth_obj = User.objects.filter(username=username).first() 

        # 下面這個條件式>> 皆非(a為空 或是 b為空) >> a跟b都不能為空>> annie0918:應該是兩個都要空才對
        if obj is None and auth_obj is None :
            print('還沒註冊過,建立 teacher_profile')
            ### 長出老師相對應資料夾 
            # 目前要長的有:放一般圖檔的資料夾user_folder(大頭照、可能之後可放宣傳圖)、未認證的資料夾unaproved_cer、
            # 已認證過的證書aproved_cer、user_info 將來可能可以放考卷檔案夾之類的、課程統一資料夾lessons、
            
            if not os.path.isdir('user_upload/teachers'):
                os.mkdir(os.path.join('user_upload/teachers'))
            if os.path.isdir(os.path.join('user_upload/teachers', user_folder)):
                # 如果已經有了這個資料夾，就刪除裡面所有項目並且重建
                shutil.rmtree(os.path.join('user_upload/teachers', user_folder))
                print('User Folder Already Existed >> Rebuild It.')
            os.mkdir(os.path.join('user_upload/teachers', user_folder))
            os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "unaproved_cer"))
            os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "aproved_cer"))
            os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "user_info")) # models裡的info_folder
            os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "lessons"))
            print('已幫老師建立5個資料夾')
            # for迴圈如果沒東西會是空的.  getlist()裡面是看前端的 multiple name

            if request.FILES.getlist("upload_snapshot"):
                for each_file in request.FILES.getlist("upload_snapshot"):
                    print('收到老師大頭照: ', each_file.name)
                    folder_where_are_uploaded_files_be ='user_upload/teachers/' + user_folder 
                    fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
                    file_exten = each_file.name.split('.')[-1]
                    fs.save('thumbnail'+'.'+ file_exten , each_file) # 檔名統一改成thumbnail開頭
                    thumbnail_dir = '/user_upload/teachers/' + user_folder + '/' + 'thumbnail'+'.'+ file_exten 
            else:
                print('沒收到老師大頭照')
                # 可能依照性別使用預設的圖片
                thumbnail_dir = ''

            # 放未認證證書的資料夾
            for each_file in request.FILES.getlist("upload_cer"):
                print('收到老師認證資料: ', each_file.name)
                folder_where_are_uploaded_files_be ='user_upload/teachers/' + user_folder + '/unaproved_cer'
                fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)

                fs.save(each_file.name, each_file)

            user_created_object = \
                User.objects.create(
                    username = username,
                    password = password,
                    is_superuser = 0,
                    first_name = '',
                    last_name = '',
                    email = '',
                    is_staff = 0,
                    is_active = 1,
                )
            user_created_object.save()
            print('老師成功建立 User.objects')
            
            teacher_profile.objects.create(
                    auth_id = user_created_object.id,
                    username = username,
                    password = password,
                    balance = 0,
                    unearned_balance = 0, # 帳戶預進帳金額，改成會計用語
                    withholding_balance = 0,
                    name = name,
                    nickname = nickname,
                    birth_date = birth_date,
                    is_male = is_male,
                    intro = intro,
                    mobile = mobile,
                    thumbnail_dir = thumbnail_dir,
                    user_folder = 'user_upload/'+ user_folder ,
                    info_folder = 'user_upload/'+ user_folder + '/user_info', 
                    tutor_experience = tutor_experience,
                    subject_type = subject_type,
                    education_1 = education_1, 
                    education_2 = education_2,
                    education_3 = education_3 ,
                    cert_unapproved = 'user_upload/'+ user_folder + '/unaproved_cer',
                    cert_approved = 'user_upload/'+ user_folder + '/aproved_cer',
                    id_approved = 0,
                    education_approved = 0,
                    work_approved = 0,
                    other_approved = 0, #其他類別的認證勳章
                    #occupation = if_false_return_empty_else_do_nothing(occupation), 
                    company = company,
                    special_exp = special_exp
            ).save()
            print('成功建立 teacher_profile')
            ## 寫入一般時間table
            # 因為models設定general_available_time與 teacher_profile 
            # 的teacher_name有foreignkey的關係
            # 因此必須用teacher_profile.objects 來建立這邊的teacher_name
            # (否則無法建立)
            teacher_object = teacher_profile.objects.get(username=username)
            general_time = request.POST.get('teacher_general_availabale_time', False)
            temp_general_time = general_time.split(';')
            print(general_time)
            for every_week in temp_general_time[0:-1]:
                temp_every_week = every_week.split(':')

                general_available_time.objects.create(
                    teacher_model = teacher_object,
                    week = temp_every_week[0],
                    time = temp_every_week[1]
                                ).save()
            print('老師成功建立 一般時間') 

            # 建立老師與system的聊天室
            chat_tool = chat_room_manager()
            chat_tool.create_system2user_chatroom(userID=teacher_object.auth_id, user_type = 'teacher')
            print('建立老師與Mr.Q 聊天室')
            # 建立group, 現在老師都是測試:3
            user_created_object.groups.add(3)

            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = user_created_object.id
            # 回傳auth_id作為data的變數
        else:
            print('此帳號已註冊過!')
            response['status'] = 'failed'
            response['errCode'] = '0'
            response['errMsg'] = 'username taken'# 使用者已註冊
            response['data'] = None
    else:
        # 資料有問題
        response['status'] = 'failed'
        response['errCode'] = '1'
        response['errMsg'] = 'wrong data'
        response['data'] = None
    
    return JsonResponse(response)

#老師個人資訊(自己看自己)
@require_http_methods(['GET'])
def return_teacher_s_profile_for_oneself_viewing(request):
    response = dict()
    teacher_auth_id = request.GET.get('userID', False)
    the_teacher_manager = teacher_manager()

    if teacher_auth_id == False:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed.'
        response['data'] = None
        return JsonResponse(response)
    
    response['status'], response['errCode'], response['errMsg'], response['data'] = \
        the_teacher_manager.return_teacher_profile_for_oneself_viewing(teacher_auth_id)
    
    return JsonResponse(response)

#老師個人資訊(公開)
@require_http_methods(['GET'])
def return_teacher_s_profile_for_public_viewing(request):
    response = dict()
    teacher_auth_id = request.GET.get('userID', False)
    the_teacher_manager = teacher_manager()

    if teacher_auth_id == False:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Received Arguments Failed.'
        response['data'] = None
        return JsonResponse(response)
    
    response['status'], response['errCode'], response['errMsg'], response['data'] = \
        the_teacher_manager.return_teacher_profile_for_public_viewing(teacher_auth_id)
    
    return JsonResponse(response)

# 登入
@require_http_methods(['POST'])
def signin(request):
    #if request.method == 'POST':
    print('收到post')
    response = {}
    username = request.POST.get('userName', False) # 當前端值有錯誤傳 null 就會是false 
    password = request.POST.get('userPwd', False)
        
    if False not in (username, password):
        user_obj = User.objects.filter(username=username).first()
        print(user_obj)
        if user_obj is None:
            # 使用者不存在
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = 'username does not exist'
            response['data'] = None
            print('使用者不存在')
        else: #使用者存在
            # 核對帳密, 當傳入的密碼=資料庫裡的密碼
            print('檢查帳密')
            if password == user_obj.password:
                # 登入 # 將登入時間輸入權限檢查的 table
                # 更新或建立 token
                time = datetime.now()
                after_14days = time + timedelta(days = 14)
                token = make_password(str(after_14days))
                # 如果有這個user, 則 token更新, 沒有則create
                user_token.objects.update_or_create(authID_object = user_obj, 
                                                defaults = {'logout_time' : after_14days,
                                                            'token' : token
                                                            },)
                print('token更新')    
                # check_type 用是不是老師來分
                user_is_teacher = teacher_profile.objects.filter(username=username).first()
                if user_is_teacher is not None:
                    print('老師')
                    user_type = 'teacher'
                    picture = user_is_teacher.thumbnail_dir
                    nickname = user_is_teacher.nickname
                    is_male = user_is_teacher.is_male
                    balance = ''
                else:
                    user_type = 'student'
                    user_is_student = student_profile.objects.filter(username=username).first()
                    picture = user_is_student.thumbnail_dir
                    nickname = user_is_student.nickname
                    is_male = user_is_student.is_male
                    balance = user_is_student.balance
                    
                # 使用者所屬的權限群組,未來一個人可能同時有好幾個所以傳list
                user_group = list()
                _user_group_set = user_obj.groups.all()
                for group_obj in _user_group_set:
                    user_group.append(group_obj.name)
                # 與系統的聊天室id
                system_chatrooID = chatroom_info_Mr_Q2user.objects.filter(user_auth_id=user_obj.id).first().id

                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
                response['data'] = {
                    'picture': picture,
                    'nickname': nickname,
                    'user_id': user_obj.id ,
                    'username': username,
                    'is_male': is_male,
                    'type': user_type,
                    'user_token': token,
                    'deposit': balance,
                    'message': '', # 是否有未讀聊天室訊息, 這邊等聊天室做了再補
                    'system_chatrooID' :system_chatrooID,
                    'user_group': user_group
                    }
                print('成功登入', response)

            else:
            # 密碼錯誤
                response['status'] = 'failed'
                response['errCode'] = '2'
                response['errMsg'] = 'wrong password'
                response['data'] = None
                print('password error')
    else:
        # 不是拿到post
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = None
        response['data'] = None
        print('wrong method')
    #return render(request, 'account/signin.html') # 測試用
    return JsonResponse(response)    


# 頁面權限檢查 目前身分有:老師/學生/訪客/會員(老師+學生)
#@require_http_methods(['POST'])
def auth_check(request):
    try:
        user_id = request.POST.get('userId', False)
        print('auth_check 檢查id:'+ str(user_id))
        url = request.POST.get('url', False)
        print('檢查網址'+ str(url))#token_from_user3 = request.META['QUERY_STRING']
        token_from_user_raw = request.headers.get('Authorization', False)
        print(token_from_user_raw) 
        # 當前端傳來空白token時(例如訪客), bearer後面會是空白的,這邊寫死來判斷
        if len(token_from_user_raw) > len('bearer '):
            # 從前端拿來的token格式: "bearer token", 為了只拿"token"因此用split切開拿後面
            token_from_user = token_from_user_raw.split(' ')[1]  
        else:
            token_from_user = ''
        
        print('token is :'+ str(token_from_user))
        page_auth = auth_check_manager()
        if user_id and  url and token_from_user is not False:
            check_data = {
                'userID' : user_id, 'url' : url, 'token': token_from_user
            }
            print('開始檢查權限~')
            response = page_auth.check_all_gate_and_responce(**check_data)
            print(response)
        else:
            response = page_auth.response_to_frontend(1)

    except Exception as e:
        print(e)
        response = page_auth.response_to_frontend(1)

    return JsonResponse(response)
            
@require_http_methods(['POST'])
def member_forgot_password(request):
    user_data_type_frontend = ['userName', 'userBirth', 'userMobile']
    pass_data_to_model_tools = dict()
    response = dict()
    for data_type in user_data_type_frontend: 
        pass_data_to_model_tools[data_type] = request.POST.get(data_type,False)
    
    the_auth_manager = auth_manager_for_password()
    
    response['status'], response['errCode'], response['errMsg'], response['data'] = \
    the_auth_manager.member_forgot_password(**pass_data_to_model_tools)
    return JsonResponse(response)

@require_http_methods(['POST'])
def member_reset_password(request):
    user_data_type_frontend = ['userID', 'newUserPwd']
    pass_data_to_model_tools = dict()
    response = dict()
    #token_from_user = request.META['QUERY_STRING']
    token_from_user_raw = request.headers.get('Authorization', False)
    print('get到token')
    print(token_from_user_raw)
    token_from_user = token_from_user_raw.split(' ')[1]
    
    #print('前端收來的token確認第一次:' + str(token_from_user))
    print('新密碼確認:', request.POST.get('newUserPwd', False))
    pass_data_to_model_tools['token'] = token_from_user
    for data_type in user_data_type_frontend: 
        pass_data_to_model_tools[data_type] = request.POST.get(data_type,False)
    print(pass_data_to_model_tools)
    the_auth_manager = auth_manager_for_password()
    
    response['status'], response['errCode'], response['errMsg'], response['data'] = \
    the_auth_manager.member_reset_password(**pass_data_to_model_tools)
    return JsonResponse(response)

#########以下是舊的views先貼過來以免 server跑不起來
'''def dev_forgot_password_1_check_username(request):
    # fotgot password step 1
    title = '忘記密碼'
    if request.method == 'POST':
        username = request.POST.get('username', False)
        if student_profile.objects.filter(username = username).count() == 1:
            # 代表有這個username
            # 儲存在session中
            request.session['username'] = username
            # print('request', request)
            # print('request.session', request.session.items())
            return redirect('forgot_pw_2')  # 原來可以直接輸入url name

        else:
            user_not_match = True
            return render(request, 'account/dev_forgot_password_1_check_username.html', locals())
    else:
        return render(request, 'account/dev_forgot_password_1_check_username.html', locals())


def dev_forgot_password_2_verification(request):
    title = '忘記密碼-認證'
    username = request.session.get('username', False)
    #print(username)
    if request.method == 'POST':
        name = request.POST.get('name', False)
        mobile_last4 = request.POST.get('mobile_last4', False)
        # birth_date = request.POST.get('birth_date', False)
        # birth_date = date(int(birth_date.split('-')[0]), int(birth_date.split('-')[1]), int(birth_date.split('-')[2]))
        # print(birth_date)
        if student_profile.objects.filter(username = username, name = name).count() == 1:
            t_user = student_profile.objects.get(username = username, name = name)
            if t_user.mobile.replace('-', '')[-4:] == mobile_last4:
                # 認證成功
                request.session['user_type'] = 'user'
                print(request.session['user_type'])
                return redirect('forgot_pw_3')

        elif teacher_profile.objects.filter(username = username, name = name).count() == 1:
            t_user = teacher_profile.objects.get(username = username, name = name)
            if t_user.mobile.replace('-', '')[-4:] == mobile_last4:
                # 認證成功
                request.session['user_type'] = 'vendor'
                print(request.session['user_type'])
                return redirect('forgot_pw_3')
        else:
            verify_fails = True
            return render(request, 'account/dev_forgot_password_2_verification.html', locals())
    else:
        return render(request, 'account/dev_forgot_password_2_verification.html', locals())


def dev_forgot_password_3_reset_password(request):
    title = '忘記密碼-重設'
    username = request.session.get('username', False)
    user_type = request.session.get('user_type', False)
    if request.method == 'POST':
        password = request.POST.get('password', False)
        re_password = request.POST.get('re_password', False)
        if password == re_password:
            if user_type == 'user':
                temp_user_profile = student_profile.objects.get(username=username)
                temp_user_profile.password = make_password(password)
                temp_user_profile.save()
                temp_user = User.objects.get(username=username)
                temp_user.password = make_password(password)
                temp_user.save()
            elif user_type == 'vendor':
                temp_vendor_profile = teacher_profile.objects.get(username=username)
                temp_vendor_profile.password = make_password(password)
                temp_vendor_profile.save()
                temp_user = User.objects.get(username=username)
                temp_user.password = make_password(password)
                temp_user.save()
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect('forgot_pw_4')
        else:
            passwords_not_match = True
            return render(request, 'account/dev_forgot_password_3_reset_password.html', locals())
    else:
        return render(request, 'account/dev_forgot_password_3_reset_password.html', locals())


def dev_forgot_password_4_update_successfully(request):
    title = '密碼設定成功'
    return render(request, 'account/dev_forgot_password_4_update_successfully.html', locals())


def admin_import_user(request):
    title = '匯入用戶資訊'
    db_manager = user_db_manager()
    folder_where_are_uploaded_files_be = 'temp' # 
    if request.method == 'POST':
        fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
        for each_file in request.FILES.getlist("files"):
            fs.save(each_file.name, each_file)
            if each_file.name.endswith(('xlsx', 'xls')):
                df = pd.read_excel(os.path.join(folder_where_are_uploaded_files_be, each_file.name))
            elif each_file.name.endswith(('txt', 'csv')):
                df = pd.read_csv(os.path.join(folder_where_are_uploaded_files_be, each_file.name))

            df.loc[:, 'password_hash'] = make_password('00000000')
            try:
                is_imported = db_manager.admin_import_user(dataframe = df)
                print(each_file.name, 'has been imported.')
            except Exception as e:
                print(each_file.name, e)
                pass
            os.unlink(os.path.join(folder_where_are_uploaded_files_be, each_file.name))
            
        db_manager.admin_create_chatrooms()
        return render(request, 'account/import_users.html', locals())
    else:
        return render(request, 'account/import_users.html', locals())'''
            

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/homepage/')

'''def for_test(request):
    title = '測試-會員登入'
    print('BEFORE')
    print(request.user.id)

    if request.method == 'POST':
        if request.POST.get('logout', False) != 'to_logout':
            username = request.POST.get('username', False)
            password = request.POST.get('password', False)
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                print('AFTER')
                print(user)
                print(user.username)
                print(user.last_login)
                print(user.date_joined)
                print(request.user.id)
                print(request.user.is_anonymous)
                print(request.user.is_authenticated)

            # if User.objects.filter(username = username).count() == 1:
                # 代表有這個username
                # user = User.objects.filter(username=username)[0]
                # real_password_hash = User.objects.filter(username=username)[0].password
                # password_match = check_password(request.POST['password'], real_password_hash)
                # user = auth.authenticate(username=username, password=password)
                # if password_match:
                auth.login(request, user)  # 將用戶登入
                return render(request, 'account/for_test.html', locals())
                # else:
                #    password_not_match = True
            else:
                user_not_match = True
        else:
            auth.logout(request)

        return render(request, 'account/for_test.html', locals())
    else:
        return render(request, 'account/for_test.html', locals())


def teacher_info_show(request):
    return render(request, 'account/teacher_member_page.html', locals())



def datepicker(request):
    print('request:',request)
    return render (request, 'account/datepicker.html' )'''


def get_time(request):
    username=request.user
    year=request.GET['year']
    month=request.GET['month']
    day=request.GET['day']
    date=year+month+day
    week=date_function(int(year),int(month),int(day)).isoweekday()
    user=teacher_profile.objects.get(username=username)

    if(specific_available_time.objects.filter(date=date).filter(user=user).exists()):
        schedule=specific_available_time.objects.get(date=date,user=user).time
    elif(general_available_time.objects.filter(week=week).filter(user=user).exists()):
        schedule=general_available_time.objects.get(week=week,user=user).time
    else:
        schedule=''
    print('schedule:',schedule)

    return HttpResponse(schedule)

def change_specific_time(request):
    username=request.user
    new_time=request.GET['new_time']
    year=request.GET['year']
    month=request.GET['month']
    day=request.GET['day']
    date=year+month+day
    print('change_date:',date)
    user=teacher_profile.objects.get(username=username)

    try:
        if(specific_available_time.objects.filter(date=date).filter(user=user).exists()):
            specific_available_time.objects.filter(date=date).filter(user=user).update(time=new_time)
        else:
            specific_available_time.objects.create(date=date,time=new_time,user=user)
        return HttpResponse('儲存成功!')
    except Exception as e:
        print(e)
        return HttpResponse('失敗!請再試一次!')

def get_general_time(request):
    week=request.GET['week']
    username=request.user
    user=teacher_profile.objects.get(username=username)

    if(general_available_time.objects.filter(week=week).filter(user=user).exists()):
        schedule=general_available_time.objects.get(week=week,user=user).time
    else:
        schedule=''
    print('schedule:',schedule)

    return HttpResponse(schedule)


def change_general_time(request):
    username=request.user
    new_time=request.GET['new_time']
    week=request.GET['week']
    user=teacher_profile.objects.get(username=username)
    try:
        if(general_available_time.objects.filter(week=week).filter(user=user).exists()):
            general_available_time.objects.filter(week=week).filter(user=user).update(time=new_time)
        else:
            general_available_time.objects.create(week=week,time=new_time,user=user)
        return HttpResponse('更新成功!')
    except Exception as e:
        print(e)
        return HttpResponse('失敗!請再試一次!')



'''def create_batch_student_users():
    response = {}
    print('StARt')
    for i in range(0, 200):
        username = 's' + str(i).rjust(5, '0') + '@edony_test.com'
        name = 'test_student_' + str(i).rjust(5, '0')
        if np.random.rand() > 0.5:
            nickname = 'ts_' + str(i).rjust(5, '0')
        else:
            nickname = name
        birth_date = date_string_2_dateformat('2000-01-01')
        is_male =  np.random.rand() > 0.5
        role = 'oneself'
        mobile = '0900-000000'
        update_someone_by_email = ''
        password = '8B6FA01313CE51AFC09E610F819250DA501778AD363CBA4F9E312A6EC823D42A'
        # 此處的password已經經過前端加密，故無需再加密
        obj = student_profile.objects.filter(username=username).first()
        auth_obj = User.objects.filter(username=username).first()
        if obj is None and auth_obj is None:
            if not os.path.isdir('user_upload/students'):
                os.mkdir(os.path.join('user_upload/students'))
            if os.path.isdir(os.path.join('user_upload/students', username)):
                # 如果已經有了這個資料夾，就刪除裡面所有項目並且重建
                shutil.rmtree(os.path.join('user_upload/students', username))
                print('User Folder Already Existed >> Rebuild It.')
            os.mkdir(os.path.join('user_upload/students', username))
            os.mkdir(os.path.join('user_upload/students/'+ username, 'info_folder'))
            # 存到 user_upload 該使用者的資料夾
            #大頭照
            if np.random.rand() > 0.5:
                pic_path = '/mnt/c/Users/User/Desktop/thumbnail'
                pic_name, pic_ext = np.random.choice(os.listdir(pic_path)).split('.')
                thumbnail_dir = '/user_upload/students/' + username + '/' + 'thumbnail'+'.'+ pic_ext
                shutil.copy(
                    os.path.join(pic_path, pic_name + '.' + pic_ext),
                    thumbnail_dir[1:]
                )
            else:
                thumbnail_dir = ''
            user_created_object = \
                User.objects.create(
                    username = username,
                    password = password,
                    is_superuser = 0,
                    first_name = '',
                    last_name = '',
                    email = '',
                    is_staff = 0,
                    is_active = 1,
                )
            # 用create()的寫法是為了知道這個user在auth裡面的id為何
            user_created_object.save()
            print('auth建立')
            print('建立新學生資料')
            student_profile.objects.create(
                auth_id = user_created_object.id,
                username = username,
                password = password,
                balance = 0,
                withholding_balance = 0,
                name = name,
                nickname = nickname,
                birth_date = birth_date,
                is_male = is_male,
                intro = '',
                role = role,
                mobile = mobile,
                user_folder = 'user_upload/'+ username,
                info_folder = 'user_upload/'+ username+ '/info_folder',
                thumbnail_dir = thumbnail_dir ,
                update_someone_by_email = update_someone_by_email
            ).save()
            print('student_profile建立: ', username)
            # 回前端
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            #response['data'] = None
        else:
            if obj is not None:
                print('此帳號已註冊過學生類別!')
            elif auth_obj is not None:
                print('此帳號已註冊到全站資料中!')
            response['status'] = 'failed'
            response['errCode'] = '0'
            response['errMsg'] = 'username taken' # 使用者已註冊
    return JsonResponse(response)


def create_batch_teacher_users():
    txt = '與三部曲不同，《銀河修理員》說的不再是小情小愛，而是像銀河寬闊的愛。在亂世中的香港，聽起來有點隱隱作痛。「平安」二字，過去這 11 個月對過多少人講？面對千瘡百孔的生活，我們想身邊所愛安好，「平安」變成了最好的祈願。香港人由烽烽火火到疫症蔓延，微小的願望看似脆弱怯懦，但道出了我們對現實的無力。\
    即使歌詞裏也描述到「誰能望穿我這種堅壯非堅壯」，死頂而已。偏偏這種死頂就是最捨身的愛。而我最喜歡的是最後一段：\
    第一次合作，黃偉文為 Dear Jane 帶來了《銀河修理員》，在這個壞透的世界，它正來得合時。本以為是一首溝女小情歌（當然看著 MV 男主角都有被迷倒一下，哈哈），但聽了幾次後有種被療癒的力量。無論經歷任何風霜，都總會一起逆風對抗。「跨宇宙又橫越洪荒」的守護，震撼之餘又帶浪漫。我們每個人都期待生命中，面對生活裡的煩惱，世界的不公，出現一位屬於自己的銀河修理員。祝你在亂流下平安。'
    txt = [_ for _ in txt]
    def get_text(txt_list, num=150):
        return ''.join(list(np.random.choice(txt_list, num, True)))    
    for i in range(45, 200):
        username = 't' + str(i).rjust(5, '0') + '@edony_test.com'
        name = 'test_teacher_' + str(i).rjust(5, '0')
        if np.random.rand() > 0.5:
            nickname = 'tt_' + str(i).rjust(5, '0')
        else:
            nickname = name
        password = '8B6FA01313CE51AFC09E610F819250DA501778AD363CBA4F9E312A6EC823D42A'
        birth_date = date_string_2_dateformat('2000-01-01')
        is_male = np.random.rand() > 0.5
        intro = get_text(txt, 150)
        mobile = '0900-000999'
        tutor_experience = np.random.choice(['1年以內','1-3年','3-5年','5-10年','10年以上'])
        subject_type = get_text(txt, 60)
        education_1 = get_text(txt, 22) # 沒填的話前端傳空的過來
        education_2 = get_text(txt, 22)
        education_3 = get_text(txt, 22)
        company = get_text(txt, 22)
        special_exp = get_text(txt, 22)
        # 一般開課時間
        user_folder = username 
        print('收到老師註冊資料', username)
        # print('判斷收到老師資料是正常的')
        # 先檢查有沒有這個username存在，存在的話會return None給obj
        obj = teacher_profile.objects.filter(username=username).first()
        auth_obj = User.objects.filter(username=username).first()
        # 下面這個條件式>> 皆非(a為空 或是 b為空) >> a跟b都不能為空>> annie0918:應該是兩個都要空才對
        if obj is None and auth_obj is None :
            print('還沒註冊過,建立 teacher_profile')
            ### 長出老師相對應資料夾 
            # 目前要長的有:放一般圖檔的資料夾user_folder(大頭照、可能之後可放宣傳圖)、未認證的資料夾unaproved_cer、
            # 已認證過的證書aproved_cer、user_info 將來可能可以放考卷檔案夾之類的、課程統一資料夾lessons、 
            if not os.path.isdir('user_upload/teachers'):
                os.mkdir(os.path.join('user_upload/teachers'))
            if os.path.isdir(os.path.join('user_upload/teachers', user_folder)):
                # 如果已經有了這個資料夾，就刪除裡面所有項目並且重建
                shutil.rmtree(os.path.join('user_upload/teachers', user_folder))
                print('User Folder Already Existed >> Rebuild It.')
            os.mkdir(os.path.join('user_upload/teachers', user_folder))
            os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "unaproved_cer"))
            os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "aproved_cer"))
            os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "user_info")) # models裡的info_folder
            os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "lessons"))
            print('已幫老師建立5個資料夾')
            # for迴圈如果沒東西會是空的.  getlist()裡面是看前端的 multiple name
            if np.random.rand() > 0.5:
                pic_path = '/mnt/c/Users/User/Desktop/thumbnail'
                pic_name, pic_ext = np.random.choice(os.listdir(pic_path)).split('.')
                thumbnail_dir = '/user_upload/teachers/' + user_folder + '/' + 'thumbnail'+'.'+ pic_ext
                shutil.copy(
                    os.path.join(pic_path, pic_name + '.' + pic_ext),
                    thumbnail_dir[1:]
                )
            else:
                thumbnail_dir = ''
            user_created_object = \
                User.objects.create(
                    username = username,
                    password = password,
                    is_superuser = 0,
                    first_name = '',
                    last_name = '',
                    email = '',
                    is_staff = 0,
                    is_active = 1,
                )
            user_created_object.save()
            print('老師成功建立 User.objects')
            teacher_profile.objects.create(
                    auth_id = user_created_object.id,
                    username = username,
                    password = password,
                    balance = 0,
                    unearned_balance = 0, # 帳戶預進帳金額，改成會計用語
                    withholding_balance = 0,
                    name = name,
                    nickname = nickname,
                    birth_date = birth_date,
                    is_male = is_male,
                    intro = intro,
                    mobile = mobile,
                    thumbnail_dir = thumbnail_dir,
                    user_folder = 'user_upload/'+ user_folder ,
                    info_folder = 'user_upload/'+ user_folder + '/user_info', 
                    tutor_experience = tutor_experience,
                    subject_type = subject_type,
                    education_1 = education_1,
                    education_2 = education_2,
                    education_3 = education_3 ,
                    cert_unapproved = 'user_upload/'+ user_folder + '/unaproved_cer',
                    cert_approved = 'user_upload/'+ user_folder + '/aproved_cer',
                    id_approved = 0,
                    education_approved = 0,
                    work_approved = 0,
                    other_approved = 0, #其他類別的認證勳章
                    #occupation = if_false_return_empty_else_do_nothing(occupation), 
                    company = company,
                    special_exp = special_exp
            ).save()
            print('成功建立 teacher_profile')
            ## 寫入一般時間table
            # 因為models設定general_available_time與 teacher_profile 
            # 的teacher_name有foreignkey的關係
            # 因此必須用teacher_profile.objects 來建立這邊的teacher_name
            # (否則無法建立)
            teacher_object = teacher_profile.objects.get(username=username)
            for every_week in range(7):
                temp_time = ','.join([ str(_) for _ in sorted(np.random.randint(0, 48, np.random.randint(0, 48, 1)))])
                if len(temp_time) > 0:
                    general_available_time.objects.create(
                        teacher_model = teacher_object,
                        week = every_week,
                        time = temp_time
                                    ).save()
            print('老師成功建立 一般時間')

def test_connect_time(request):
    from time import time
    s_time = time()
    _ = teacher_profile.objects.all().count()
    return HttpResponse(str(time() - s_time) + ' seconds,   for' + str(_) + ' teachers.')'''


@require_http_methods(['POST'])
def feedback_view_function(request):
    response = dict()

    who_are_you = request.POST.get('who_are_you', False)
    contact = request.POST.get('contact', False)
    problem = request.POST.get('problem', False)
    on_which_page = request.POST.get('on_which_page', False)
    is_signed_in = request.POST.get('is_signed_in', False) in ['true', True, 'True']

    if False not in (who_are_you, contact, problem, on_which_page):
        # 檢查一下傳輸有沒有問題

        # 將客戶反應的資料存進DB
        feedback_record = feedback.objects.create(
            who_are_you=who_are_you,
            contact=contact,
            problem=problem,
            on_which_page=on_which_page,
            is_signed_in=is_signed_in
        )
        feedback_record.save()
        response['status'] = 'success'
        response['errCode'] = None
        response['errMsg'] = None
        response['data'] = '謝謝您告訴我們這件事，我們會火速處理、並協助您解決這個問題，請再留意您的Email或手機唷。'
    else:
        # 傳輸有問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Error: Received None.'
        response['data'] = None

    return JsonResponse(response)