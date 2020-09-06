from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
import json, os
from django.middleware.csrf import get_token

from account.models import dev_db, student_profile, teacher_profile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password  # 這一行用來加密密碼的

def is_int(target):
    try:
        as_int = int(target)
        if as_int == float(target):
            return True
        else:
            return False
    except:
        return False


def date_string_2_dateformat(target_string):
    from datetime import date as date_function
    if not target_string == False:
        try:
            if len(target_string) == 8 and is_int(target_string):
                _year, _month, _day = int(birth_date[:4]), int(birth_date[4:6]), int(birth_date[-2:])
                return date_function(_year, _month, _day)
            else:
                return False
        except Exception as e:
            print(e)
            return False
    else:
        return False

if_false_return_empty_else_do_nothing = lambda x: '' if not x else x
# 上面這段函式，主要是用來處理類似「工作經歷」之類的欄位，
# 當user不打字時，經過我們的get(, False)後會轉成False，
# 然而我不想要以'0'的方式將值存入資料庫中，因此透過這個函式再轉成''

@require_http_methods(['POST'])
def homepage_recommendList(request):
    qty = request.POST.get('qty', False)
    response = {}
    
    data = []
    try:
        if is_int(qty):
            for _ in range(int(qty)):
                data.append(
                    {
                        'id': _,
                        'title': '馬鈴薯哥哥拉丁語' + str(_),
                        'introduction': '超棒拉丁語，聽得懂不用錢之' + str(_),
                        'img_url': 'user_upload/' + 's'+ str(_) + 'ats' + str(_) + '/snapshot.png',
                    }
                )
            return JsonResponse(data, safe=False)
    except Exception as e:
        response['msg'] = str(e)
        return JsonResponse(data)

    
@require_http_methods(['GET'])
def homepage_api_getBannerBar(request):
    data = []
    img_path = 'website_assets/homepage/'
    # 之後再看這個路徑該怎麼修比較好
    for i, desktop_img in enumerate(os.listdir(os.path.join(img_path, 'desktop'))):
        data.append(
            {
                'type': 'pc',
                'sort': str(i),
                'img_url': img_path + '/desktop/' + desktop_img,
            }
        )
    for i, mobile_img in enumerate(os.listdir(os.path.join(img_path, 'mobile'))):
        data.append(
            {
                'type': 'mobile',
                'sort': str(i),
                'img_url': img_path + '/mobile/' + mobile_img,
            }
        )
    return JsonResponse(data, safe=False)


@require_http_methods(['GET'])
def get_csrf_token(request):
    csrf_token = get_token(request)
    response = {}
    response['csrf_token'] = csrf_token
    return JsonResponse(response)



# 以下只是用來做測試的而已
@require_http_methods(['GET'])
def create_dev_db_user(request):
    response = {}
    username = request.GET.get('username', False)
    password = request.GET.get('password', False)
    name = request.GET.get('name', False)
    birth_date = date_string_2_dateformat(request.GET.get('birth_date', False))
    is_male = request.GET.get('is_male', None)
    # print(is_male)
    # http://127.0.0.1:8000/api/create_dev_db_user/?username=testUser3&password=1111&name=tata3&birth_date=19901225&is_male=1
    if int(is_male) == 0:
        is_male = False
    else:
        is_male = True
    if False not in [username, password, name, birth_date] and is_male is not None:
        dev_db.objects.create(
            username = username,
            password = password,
            name = name,
            birth_date = date_function(_year, _month, _day),
            is_male = is_male
        )
        response['status'] = 'success'
        response['errCode'] = None
        response['errMsg'] = None
        response['data'] = None
        return JsonResponse(response)
    else:
        response['status'] = 'failed'
        response['errCode'] = '1'
        response['errMsg'] = 'not match'
        response['data'] = None
        return JsonResponse(response)
        

@require_http_methods(['GET'])
def show_users(request):
    all_users = dev_db.objects.all()
    data = []
    for each_user in all_users:
        data.append({
            'username': each_user.username,
            'password': each_user.password,
            'name': each_user.name,
            'birth_date': each_user.birth_date,
            'is_male': each_user.is_male
        })
    return JsonResponse(data, safe=False)


@require_http_methods(['POST'])
def create_a_student_user(request):
    response = {}
    username = request.POST.get('username', False)
    # 此處的password已經經過前端加密，故無需再加密
    password = request.POST.get('password', False)
    name = request.POST.get('name', False)
    nickname = request.POST.get('nickname', False)
    if not nickname:
        nickname = name
    birth_date = date_string_2_dateformat(request.POST.get('birth_date', False))
    is_male = request.POST.get('is_male', None)
    if int(is_male) == 0:
        is_male = False
    else:
        is_male = True
    # intro , 註冊時不需要填寫
    role = request.POST.get('role', False)
    mobile = request.POST.get('mobile', False)
    update_someone_by_email = request.POST.get('update_someone_by_email', False)

    if False not in [username, password, name, birth_date, role, mobile, 
    update_someone_by_email] and is_male is not None:
        # 先檢查有沒有這個username存在，存在的話會return None給obj
        obj = student_profile.objects.filter(username=username).first()
        auth_obj = User.objects.filter(username=username).first()
        # 下面這個條件式>> 皆非(a為空 或是 b為空) >> a跟b都不能為空
        if not (obj is None or auth_obj is None):
            student_profile.objects.create(
                username = username,
                password = password,
                name = name,
                nickname = nickname,
                balance = 0,
                withholding_balance = 0,
                birth_date = birth_date,
                is_male = is_male,
                role = role,
                mobile = mobile,
                update_someone_by_email = update_someone_by_email
            ).save()

            User.objects.create(
                username = username,
                password = password,
                is_superuser = 0,
                first_name = '',
                last_name = '',
                email = '',
                is_staff = 0,
                is_active = 1,
            ).save()
            
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = None
        else:
            response['status'] = 'failed'
            response['errCode'] = '0'
            response['errMsg'] = 'username taken' # 使用者以註冊
            response['data'] = None
    else:
        # 資料有問題
        response['status'] = 'failed'
        response['errCode'] = '1'
        response['errMsg'] = 'wrong data'
        response['data'] = None
    
    return JsonResponse(response)



##### 老師區 #####
@require_http_methods(['POST'])
def create_a_teacher_user(request):
    response = {}
    username = request.POST.get('username', False) # 當前端沒有值 就會是false ..
    password = request.POST.get('password', False)
    # origin >> balance = request.POST.get('balance', False)
    # origin >> withholding_balance = request.POST.get('withholding_balance', False)
    # 不用寫上面那兩個，因為一開始老師註冊的時候不會有這兩個資訊，我們寫入db時主動帶入0就好了
    name = request.POST.get('name', False)
    nickname = request.POST.get('nickname', False)
    if not nickname:
        nickname = name
    birth_date = date_string_2_dateformat(request.POST.get('birth_date', False))
    is_male = request.POST.get('is_male', None)
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
    mobile = request.POST.get('mobile', False)
    # origin >> picture_folder = request.POST.get('picture_folder', False)
    # 我們自己建的，不需要前端/user給我們資料
    picture_folder = 'some/where/we/create/by/username'
    # origin >> info_folder = request.POST.get('info_folder', False) # 資料夾路徑，存放個人檔案（暫不使用）
    # 我們自己建的，不需要前端/user給我們資料
    info_folder = 'some/where/we/create/by/username'
    tutor_experience = request.POST.get('tutor_experience', False)
    subject_type = request.POST.get('subject_type', False)
    education_1 = request.POST.get('education_1', False)
    education_2 = request.POST.get('education_2', False)
    education_3 = request.POST.get('education_3', False)
    # origin >> cert_unapproved = request.POST.get('cert_unapproved', False)
    # origin >> cert_approved = request.POST.get('cert_approved', False)
    # origin >> id_approved = request.POST.get('id_approved', False)
    # origin >> education_approved = request.POST.get('education_approved', False)
    # origin >> work_approved = request.POST.get('work_approved', False)
    # origin >> other_approved = request.POST.get('other_approved', False)  #其他類別的認證勳章
    cert_unapproved = 'some/where/we/create/by/username'
    cert_approved = 'some/where/we/create/by/username'
    id_approved = 'some/where/we/create/by/username'
    education_approved = 'some/where/we/create/by/username'
    work_approved = 'some/where/we/create/by/username'
    other_approved = 'some/where/we/create/by/username'
    # 以上的原因也一樣，因為這些性質是資料夾路徑(我們自己建的)，不需要前端/user給我們資料
    # 但我們可能需要一些變數，來跟前端拿取user上傳的資料，不過我們頁面只有一個上傳欄位，
    # 或許我們先經過人工審核後再決定要分別放到哪一個資料夾去？
    # 另外，我們也要跟GARY確認一下user註冊時的上傳資料會用什麼形式讓後端接收，
    # 目前這個api裡面還沒有這個機制。
    occupation = request.POST.get('occupation', False)
    company = request.POST.get('company', False)

    # print(is_male)
    # # http://127.0.0.1:8000/api/create_teacher/?username=testUser3&password=1111&name=tata3&birth_date=19901225&is_male=1

    if False not in [
        username, password, name, intro, subject_type, mobile,
        tutor_experience, subject_type
    ] and is_male is not None:
        # 先檢查有沒有這個username存在，存在的話會return None給obj
        # origin >> obj = student_profile.objects.filter(username=username).first()
        # tata: 要改成老師的資料庫
        obj = teacher_profile.objects.filter(username=username).first()
        auth_obj = User.objects.filter(username=username).first() #? .first是甚麼意思
        # 下面這個條件式>> 皆非(a為空 或是 b為空) >> a跟b都不能為空
        if not (obj is None or auth_obj is None):
            # origin >> student_profile.objects.create(
            teacher_profile.objects.create(
                    username = username,
                    password = password,
                    balance = 0,
                    # origin future_balance = 0,
                    unearned_balance = 0, # 帳戶預進帳金額，改成會計用語
                    withholding_balance = 0,
                    name = name,
                    nickname = nickname,
                    birth_date = birth_date,
                    is_male = is_male,
                    intro = intro,
                    mobile = mobile,
                    picture_folder = picture_folder,
                    info_folder = info_folder,
                    tutor_experience = tutor_experience,
                    subject_type = subject_type,
                    education_1 = education_1,
                    education_2 = education_2,
                    education_3 = education_3 ,
                    cert_unapproved = cert_unapproved,
                    cert_approved = cert_approved,
                    id_approved = id_approved,
                    education_approved = education_approved,
                    work_approved = work_approved,
                    other_approved = other_approved, #其他類別的認證勳章
                    occupation = if_false_return_empty_else_do_nothing(occupation), 
                    company = if_false_return_empty_else_do_nothing(company)
            ).save()

            User.objects.create(
                username = username,
                password = password,
                is_superuser = 0,
                first_name = '',
                last_name = '',
                email = '',
                is_staff = 0,
                is_active = 1,
            ).save()
                      
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = None
        
        else:
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