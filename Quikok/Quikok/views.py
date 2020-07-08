from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
def homepage(request):
    return render(request, 'homepage.html')

def base_layout(request):
    return render(request, 'base_layout.html')