from django.conf.urls import url, include
from django_api import views
from django.urls import path


urlpatterns = [
    path('course/recommendList/', views.homepage_recommendList),
    path('getBannerBar/', views.homepage_api_getBannerBar),
]