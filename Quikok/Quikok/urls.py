from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('homepage/', views.homepage)
]
