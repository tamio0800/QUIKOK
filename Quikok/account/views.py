from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password  # 這一行用來加密密碼的
from .model_tools import user_db_manager
from django.contrib.auth.models import User
from account.models import user_token,student_profile, teacher_profile, specific_available_time, general_available_time
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage
from account.models import dev_db
from datetime import date as date_function
import pandas as pd
import os
# FOR API
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
import json
from django.middleware.csrf import get_token
from datetime import datetime, timedelta
import shutil

def is_num(target):
    try:
        int(target)
        if int(target) == float(target):
            return True
        else:
            return False
    except:
        return False


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
            # 目前學生暫時沒開放此上傳功能 ?? 10/13 what?

            each_file = request.FILES.get("upload_snapshot")
            if each_file :
                print('收到學生大頭照: ', each_file.name)
                folder_where_are_uploaded_files_be ='user_upload/students/' + username
                fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
                file_exten = each_file.name.split('.')[-1]
                fs.save('thumbnail'+'.'+ file_exten , each_file) # 檔名統一改成thumbnail開頭
                thumbnail_dir = 'user_upload/students/' + username + '/' + 'thumbnail'+'.'+ file_exten
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
            print('student_profile建立')


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



##### 老師區 #####
@require_http_methods(['POST'])
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
    info_folder = 'some/where/we/create/by/username'
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
                    thumbnail_dir = 'user_upload/teachers/' + user_folder + '/' + each_file.name

    
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
            teacher_id = teacher_profile.objects.get(username=username)
            general_time = request.POST.get('teacher_general_availabale_time', False)
            temp_general_time = general_time.split(';')
            print(general_time)
            for every_week in temp_general_time[0:-1]:
                temp_every_week = every_week.split(':')

                general_available_time.objects.create(
                    teacher_id = teacher_id,
                    week = temp_every_week[0],
                    time = temp_every_week[1]
                                ).save()
            print('老師成功建立 一般時間')    

            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = None
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
                token = make_password(after_14days)
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
                    }
                print('成功登入', response)

            else:
            # 密碼錯誤
                response['status'] = 'failed'
                response['errCode'] = '2'
                response['errMsg'] = 'wrong password'
                response['data'] = None
                print('password error')
        #else:
        #    response['status'] = 'failed'
        #    response['errCode'] = '3'
        #    response['errMsg'] = 'get nothing'
        #    response['data'] = None
        #    print('get nothing')
    else:
        # 不是拿到post
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = None
        response['data'] = None
        print('wrong method')
    #return render(request, 'account/signin.html') # 測試用
    return JsonResponse(response)    


# 頁面權限檢查 目前身分有:老師/學生/訪客
#@require_http_methods(['POST'])
def auth_check(request):
    response = {}
    user_id = request.POST.get('userId', False)
    print('檢查id格式'+ str(user_id))
    url = request.POST.get('url', False)
    print('檢查網址'+ url)
    #token_from_user = request.POST.get('token', False)
    #token_from_user = request.META.get('Authorization', False)
    token_from_user = request.META['QUERY_STRING']
    token_clean =  token_from_user.split('=')[0]
    print('token is :'+ str(token_clean))
    response['status'] = 'success'
    response['errCode'] = None
    response['errMsg'] = None
    response['data'] = {
        'authority' : True 
    }
    return JsonResponse(response)
    #time = datetime.now()
    #user = user_token.objects.filter(authID_object = user_id).first()
    
    #暫時先註記，目前訪客id給-1，所以會找不到對應的資料，後續再修正
    #token_in_db = user.token
    #logout_date = user.logout_time
    #logout_only_date = logout_date.split(' ')[0] # 0是日期, 1是小時
    #logout_datetime_type = datetime.strptime(logout_only_date,"%Y-%m-%d")
    #time_has_passed = logout_datetime_type - time 
    
    # if url是需要權限的才需要登入
    '''if user_id is not False: 
        # 超過十四天未登入,直接沒有權限、需再登入
        if time_has_passed.days > 13:
            response['status'] = 'success'
            response['errCode'] = '0'
            response['errMsg'] = 'more than 14 days'
            response['data'] = {'authority': False}

        else:
            if token_from_user == token_in_db:
                # 進入檢查該網頁權限程序
                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
                response['data'] = {
                'authority' : True 
                }
                print('成功登入', response) 
            else:
                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = 'token error'
                response['data'] = {
                'authority' : True 
                }
                print('請重新登入', response)
    
    else: # 可能是訪客或是沒收到資訊
        if url and token_from_user:
            # 進檢查程序
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = {
            'authority' : True 
            }
        else:
            response['status'] = 'failed'
            response['errCode'] = None
            response['errMsg'] = 'not received data'
            response['data'] = None
            print('失敗', response)
    return JsonResponse(response)'''

        






#########以下是舊的views先貼過來以免 server跑不起來

def signup(request):
    title = '會員註冊'
   
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST.get('password', False)
        password_hash = make_password(password)
        name = request.POST['name'].strip()
        nickname = request.POST['nickname'].strip()
        birth_date = request.POST.get('birth_date', False)
        if birth_date != False and is_num(birth_date):
            if len(str(birth_date)) == 8:
                birth_date = date_function(
                    int(str(birth_date)[:4]),
                    int(str(birth_date)[4:6]),
                    int(str(birth_date)[-2:])
                    )
            else:
               birth_date = None
        else:
            birth_date = None 
        # birth_date = '1990-12-25' # request.POST['birth_date']
        is_male = request.POST['is_male']
        role = request.POST['role']
        mobile = request.POST['mobile'].strip()
        user_folder = 'to_be_deleted'
        update_someone_by_email = request.POST['update_someone_by_email'].strip()

        db_manager = user_db_manager()        
        is_successful = \
            db_manager.create_user(
                user_type = 'user',
                username = username,
                password_hash = password_hash,
                name = name,
                nickname = nickname,
                birth_date = birth_date,
                is_male = is_male,
                role = request.POST['role'],
                mobile = request.POST['mobile'],
                user_folder = 'to_be_deleted',
                update_someone_by_email = request.POST['update_someone_by_email'],
            )
        if is_successful:
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
        else:
            username_taken = True
        return render(request, 'account/signup.html', locals())
    else:
        return render(request, 'account/signup.html', locals())



def dev_forgot_password_1_check_username(request):
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
        return render(request, 'account/import_users.html', locals())
            

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/homepage/')

def for_test(request):
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
    return render (request, 'account/datepicker.html' )


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