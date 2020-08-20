from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('signup/', views.signup, name='to_signup'),
    path('signin/', views.signin, name='to_signin'),
    path('logout/', views.logout, name='to_logout'),
    path('test/', views.for_test),
    path('dev_import_vendor/', views.dev_import_vendor),
    path('dev_forgot_password_1/', views.dev_forgot_password_1_check_username, name='forgot_pw_1'),
    path('dev_forgot_password_2/', views.dev_forgot_password_2_verification, name='forgot_pw_2'),
    path('dev_forgot_password_3/', views.dev_forgot_password_3_reset_password, name='forgot_pw_3'),
    path('dev_forgot_password_4/', views.dev_forgot_password_4_update_successfully, name='forgot_pw_4'),
]