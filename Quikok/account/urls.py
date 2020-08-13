from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('user_signup/', views.signup),
    path('dev_user_signin/', views.dev_signin),
    path('dev_forgot_password/', views.dev_forgot_password),
    path('dev_import_vendor/', views.dev_import_vendor),
]