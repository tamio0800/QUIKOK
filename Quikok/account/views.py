from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password  # 這一行用來加密密碼的


# Create your views here.
def signup(request):
    title = '開課! Quikok - 會員註冊'
    return render(request, 'account/user_signup.html', locals())

def dev_signup(request):
    title = '開課! Quikok - 會員註冊'
    if request.method == 'POST':
        origin_pw = request.POST['pw']
        new_pw = make_password(origin_pw)
        return render(request, 'account/dev_user_signup_backend.html', locals())
    return render(request, 'account/dev_user_signup_backend.html', locals())
