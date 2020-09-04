from django.conf.urls import url, include
from django_api import views
from django.urls import path


urlpatterns = [
    path('course/recommendList/', views.homepage_recommendList),
    path('getBannerBar/', views.homepage_api_getBannerBar),
    path('get_csrf_token/', views.get_csrf_token),
    path('create_dev_db_user/', views.create_dev_db_user),
    path('show_users/', views.show_users),
    #path('create_a_student_user/', views.create_a_student_user),
]