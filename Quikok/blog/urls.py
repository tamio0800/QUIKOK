from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('hello_blog/', views.hello_blog, name='hello_blog'),
]
