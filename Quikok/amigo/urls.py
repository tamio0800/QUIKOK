from .import views
from django.urls import path

urlpatterns = [
    path('', views.main_amigo, name='main_amigo'),
]