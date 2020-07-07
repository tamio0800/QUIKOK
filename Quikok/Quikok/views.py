from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

#首頁
#@login_required(login_url = '/accounts/login/')
def homepage(request):
    # 指定某些帳號群組才能看到網頁部分內容
    #user = request.user # 當前登入的user
    #g_val = request.user.groups.values_list('name',flat = True) # QuerySet Object
    #pyli = list(g_val) # user 屬於哪些group
    # 如果 user 加入的 group中有符合有權限的群組
    #if "happy_manager" in pyli:
    #    return render(request, 'homepage.html', 
    #    {'title':'首頁',
    #    'Auth':'happy_manager'})
    #else:
    return render(request, 'homepage.html')