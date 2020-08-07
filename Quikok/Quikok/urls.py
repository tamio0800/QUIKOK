from django.conf.urls import include, url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chatroom.urls')),
    path('homepage/', views.homepage, name='home'),
    path('base_layout/', views.base_layout),
    path('account/', include('account.urls')),
    path('lesson/', include('lesson.urls')),
    path('test/', views.test_page)
]
