from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('user_signup/', views.signup),
    path('test/', views.for_test),
    path('dev_user_signin/', views.dev_signin),
    path('dev_import_vendor/', views.dev_import_vendor),
    path('dev_forgot_password_1/', views.dev_forgot_password_1_check_username),
    path('dev_forgot_password_2/', views.dev_forgot_password_2_verification),
    path('dev_forgot_password_3/', views.dev_forgot_password_3_reset_password),
    path('dev_forgot_password_4/', views.dev_forgot_password_4_update_successfully),
]