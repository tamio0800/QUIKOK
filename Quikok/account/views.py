from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password  # 這一行用來加密密碼的
from .model_tools import user_db_manager
from django.contrib.auth.models import User
from account.models import student_profile, teacher_profile
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage

import pandas as pd
import os
from datetime import date

def is_num(target):
    try:
        int(target)
        if int(target) == float(target):
            return True
        else:
            return False
    except:
        return False

# Create your views here.
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
                birth_date = date(
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
        picture_folder = 'to_be_deleted'
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
                picture_folder = 'to_be_deleted',
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


def signin(request):
    title = '會員登入'
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        remember_me = request.POST.get('remember_me', False)
        if remember_me != 1:
            request.session.set_expiry(0)
            # 不留存cookies
        else:
            request.session.set_expiry(None)
            # 如果value等于0，那么session将在web浏览器关闭后就直接过期。
            # 如果value等于None，那么session将用settings.py中设置的全局过期字段SESSION_COOKIE_AGE，这个字段默认是14天，也就是2个礼拜。
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            # print(user)
        # if User.objects.filter(username = username).count() == 1:
            # 代表有這個username
            # user = User.objects.filter(username=username)[0]
            # real_password_hash = User.objects.filter(username=username)[0].password
            # password_match = check_password(request.POST['password'], real_password_hash)
            # user = auth.authenticate(username=username, password=password)
            # if password_match:
            auth.login(request, user)  # 將用戶登入
            return HttpResponseRedirect('/homepage/')
            # else:
            #    password_not_match = True
        else:
            user_not_match = True

        return render(request, 'account/signin.html', locals())
    else:
        return render(request, 'account/signin.html', locals())


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
    folder_where_are_uploaded_files_be = 'temp'
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