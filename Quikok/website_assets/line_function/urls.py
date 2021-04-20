from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls import include

urlpatterns = [
    path('callback/', views.callback),
    path('upload/<str:file>', views.upload_file),
]