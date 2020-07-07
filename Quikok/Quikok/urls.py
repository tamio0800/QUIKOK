from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('homepage/', views.homepage),
    path('account/', include('account.urls')),
]

urlpatterns += staticfiles_urlpatterns()
