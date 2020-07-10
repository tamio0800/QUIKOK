from django.shortcuts import render, redirect


# Create your views here.
def signup(request):
    title = '開課! Quikok - 會員註冊'
    return render(request, 'account/user_signup.html', locals())

def dev_signup(request):
    title = '開課! Quikok - 會員註冊'
    if request.method == 'POST':
        print(request.POST['username'])
        print(request.POST['password'])
        print(request.POST['re_password'])
    return render(request, 'account/dev_user_signup.html', locals())