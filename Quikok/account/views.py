from django.shortcuts import render, redirect


# Create your views here.
def signup(request):
    return render(request, 'account/user_signup.html')

def dev_signup(request):
    if request.method == 'POST':
        print(request.POST['username'])
        print(request.POST['password'])
        print(request.POST['re_password'])
    return render(request, 'account/dev_user_signup.html')