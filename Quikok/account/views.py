from django.shortcuts import render, redirect


# Create your views here.
def signup_function(request):
    return render(request, 'account/test_user_form.html')