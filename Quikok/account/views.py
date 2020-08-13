from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password  # 這一行用來加密密碼的
from .model_tools import user_db_manager
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage

import pandas as pd
import os

# Create your views here.
def signup(request):
    title = '會員註冊'
    
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password_hash = make_password(request.POST['password'])
        name = request.POST['name'].strip()
        nickname = request.POST['nickname'].strip()
        birth_date = request.POST['birth_date']
        is_male = request.POST['is_male']
        role = request.POST['role']
        mobile = request.POST['mobile'].strip()
        picture_folder = 'to_be_deleted'
        update_someone_by_email = request.POST['update_someone_by_email'].strip()

        db_manager = user_db_manager()        
        ret = \
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
        if not ret:
            already_taken_username = username
        

        return render(request, 'account/user_signup.html', locals())
    return render(request, 'account/user_signup.html', locals())

def dev_signin(request):
    title = '會員登入'
    if request.method == 'POST':
        username = request.POST['username']
        if len(User.objects.filter(username = username)) == 1:
            # 代表有這個username
            user = User.objects.filter(username=username)[0]
            real_password_hash = User.objects.filter(username=username)[0].password
            password_match = check_password(request.POST['password'], real_password_hash)
            if password_match:
                auth.login(request, user)  # 將用戶登入
                return HttpResponseRedirect('/homepage/')
            else:
                password_not_match = True
                render(request, 'account/dev_user_signin.html', locals())
        else:
            user_not_match = True
            render(request, 'account/dev_user_signin.html', locals())
    else:
        return render(request, 'account/dev_user_signin.html', locals())


def dev_forgot_password(request):
    title = '忘記密碼'
    if request.method == 'POST':
        username = request.POST['username']
        if len(User.objects.filter(username = username)) == 1:
            # 代表有這個username
            user = User.objects.filter(username=username)[0]
            real_password_hash = User.objects.filter(username=username)[0].password
            password_match = check_password(request.POST['password'], real_password_hash)
            if password_match:
                auth.login(request, user)  # 將用戶登入
                return HttpResponseRedirect('/homepage/')
            else:
                password_not_match = True
                render(request, 'account/dev_user_forgot_password.html', locals())
        else:
            user_not_match = True
            render(request, 'account/dev_user_forgot_password.html', locals())
    else:
        return render(request, 'account/dev_user_forgot_password.html', locals())

def dev_import_vendor(request):
    title = '批次上傳老師資料'

    db_manager = user_db_manager()
    folder_where_are_uploaded_files_be = 'temp_files'
    if request.method == 'POST':
        fs = FileSystemStorage()
        for each_file in request.FILES.getlist("files"):
            fs.save(each_file.name, each_file)

            if each_file.name.endswith(('xlsx', 'xls')):
                df = pd.read_excel(os.path.join(folder_where_are_uploaded_files_be, each_file.name))
                df.loc[:, 'password_hash'] = make_password('00000000')
                print(df.password_hash.tolist())
                try:
                    is_imported = db_manager.dev_import_vendor(dataframe = df)
                    print(each_file.name, 'has been imported.')
                except Exception as e:
                    print(each_file.name, e)
                    pass
            os.unlink(os.path.join(folder_where_are_uploaded_files_be, each_file.name))
            return render(request, 'account/dev_import_vendor.html', locals())
    else:
        return render(request, 'account/dev_import_vendor.html', locals())
            

