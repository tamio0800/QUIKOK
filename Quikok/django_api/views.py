from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
import json, os
from django.middleware.csrf import get_token
from datetime import date as date_function

from account.models import dev_db, student_profile, teacher_profile


def is_int(target):
    try:
        as_int = int(target)
        if as_int == float(target):
            return True
        else:
            return False
    except:
        return False


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
    birth_date = request.GET.get('birth_date', False)
    is_male = request.GET.get('is_male', None)
    # print(is_male)
    # http://127.0.0.1:8000/api/create_dev_db_user/?username=testUser3&password=1111&name=tata3&birth_date=19901225&is_male=1
    if int(is_male) == 0:
        is_male = False
    else:
        is_male = True
    if False not in [username, password, name, birth_date] and is_male is not None:
        # birth_date預期會是長這樣>> 19900101
        _year, _month, _day = int(birth_date[:4]), int(birth_date[4:6]), int(birth_date[-2:])
        dev_db.objects.create(
            username = username,
            password = password,
            name = name,
            birth_date = date_function(_year, _month, _day),
            is_male = is_male
        )
        response['status'] = 'success'
        response['errCode'] = 'null'
        response['errMsg'] = 'null'
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


#@require_http_methods(['GET'])
#def create_a_student_user(request):

##### 老師區
@require_http_methods(['GET'])
def create_teacher(request):
    response = {}
    username = request.GET.get('username', False)
    password = request.GET.get('password', False)
    balance = request.GET.get('name', False)
    withholding_balance = request.GET.get('name', False)
    name = request.GET.get('name', False)
    nickname = request.GET.get('nickname', False)
    birth_date = request.GET.get('birth_date', False)
    is_male = request.GET.get('is_male', None)
    intro = request.GET.get('is_male', None)
    mobile = request.GET.get('is_male', None)
    # picture_folder = request.GET.get('is_male', None)
    picture_folder = request.GET.get('is_male', None)
    info_folder = request.GET.get('is_male', None)
    tutor_experience = request.GET.get('is_male', None)
    subject_type = request.GET.get('is_male', None)
    education_1 = request.GET.get('is_male', None)
    education_2 = request.GET.get('is_male', None)
    education_3 = request.GET.get('is_male', None)
    cert_unapproved = request.GET.get('is_male', None)
    cert_approved = request.GET.get('is_male', None)
    id_approved = request.GET.get('is_male', None)
    education_approved = request.GET.get('is_male', None)
    work_approved = request.GET.get('is_male', None)
    other_approved = request.GET.get('is_male', None)  #其他類別的認證勳章
    occupation = request.GET.get('is_male', None)
    company = request.GET.get('is_male', None)
    date_join = request.GET.get('is_male', None)


    # print(is_male)
    # # http://127.0.0.1:8000/api/create_teacher/?username=testUser3&password=1111&name=tata3&birth_date=19901225&is_male=1
    if int(is_male) == 0:
        is_male = False
    else:
        is_male = True
    if False not in [username, password, name, birth_date] and is_male is not None:
        # birth_date預期會是長這樣>> 19900101
        _year, _month, _day = int(birth_date[:4]), int(birth_date[4:6]), int(birth_date[-2:])
        teacher_profile.objects.create(
            username = username,
            password = password,
            name = name,
            birth_date = date_function(_year, _month, _day),
            is_male = is_male
        )
        response['status'] = 'success'
        response['errCode'] = 'null'
        response['errMsg'] = 'null'
        response['data'] = None
        return JsonResponse(response)
    else:
        response['status'] = 'failed'
        response['errCode'] = '1'
        response['errMsg'] = 'not match'
        response['data'] = None
        return JsonResponse(response)
