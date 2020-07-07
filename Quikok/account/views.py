from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

# Create your views here.
