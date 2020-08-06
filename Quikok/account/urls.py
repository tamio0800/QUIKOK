from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('user_signup/', views.signup),
    path('dev_user_signup/', views.dev_signup)
]