from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
def homepage(request):
    title = '開課! Quikok'
    return render(request, 'homepage.html', locals())

def base_layout(request):
    return render(request, 'base_layout.html')

def test_page(request):
    return render(request, 'test.html')