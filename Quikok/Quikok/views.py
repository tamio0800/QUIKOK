from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import os

# Create your views here.
def homepage(request):
    title = '開課! Quikok'
    return render(request, 'homepage.html', locals())

def base_layout(request):
    return render(request, 'base_layout.html')

def test_page(request):
    from django.core.files.storage import FileSystemStorage

    username = 's1ats1'
    folder_where_are_uploaded_files_be = 'user_upload/'+ username
    if request.method == 'POST':
        
        user_folder = username

        os.mkdir(os.path.join('user_upload', user_folder))
        os.mkdir(os.path.join('user_upload/'+ user_folder, "unaproved_cer"))
        os.mkdir(os.path.join('user_upload/'+ user_folder, "aproved_cer"))

        # for迴圈如果沒東西會是空的.  getlist()裡面是看前端的 multiple name
        for each_file in request.FILES.getlist("upload_snapshot"):
            print('收到老師大頭照: ', each_file.name)
            folder_where_are_uploaded_files_be ='user_upload/' + user_folder 
            fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
            fs.save(each_file.name, each_file)
        # 放未認證證書的資料夾
        for each_file in request.FILES.getlist("upload_cer"):
            print('收到老師認證資料: ', each_file.name)
            folder_where_are_uploaded_files_be ='user_upload/' + user_folder + '/unaproved_cer'
            fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
            fs.save(each_file.name, each_file)

    return render(request, 'test.html')

    


