from django.shortcuts import render, redirect


# Create your views here.
def signup_function(request):
    return render(request, 'account/user_signup.html')

def test_func(request):
    return render(request, 'account/dev_user_signup.html')