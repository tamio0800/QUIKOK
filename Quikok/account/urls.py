from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('user_signup/', views.signup_function)
]