from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password  # 這一行用來加密密碼的


# Create your views here.
def signup(request):
    title = '開課! Quikok - 會員註冊'
    return render(request, 'account/user_signup.html', locals())

def dev_signup(request):
    title = '開課! Quikok - 會員註冊'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_hash = make_password(password)
        name = request.POST['name']
        birth_date = request.POST['birth_date']
        is_male = request.POST['is_male']

        return render(request, 'account/dev_user_signup_backend.html', locals())
    return render(request, 'account/dev_user_signup_backend.html', locals())


