from django.conf.urls import include, url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path, include, re_path  # 新增的
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView  # 新增的


urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chatroom.urls')),
    path('homepage/', views.homepage, name='home'),
    path('base_layout/', views.base_layout),
    path('account/', include('account.urls')),
    path('api/lesson/', include('lesson.urls')),
    path('test/', views.test_page),
    # path('api/course/recommendList', views.homepage_api_recommendList),
    # path('api/getBannerBar', views.homepage_api_getBannerBar),
    path('api/', include('django_api.urls')),
    re_path(r'^$', TemplateView.as_view(template_name="index.html")),  # 新增的
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)