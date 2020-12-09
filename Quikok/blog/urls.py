from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('main_blog/', views.main_blog, name='main_blog'),
    #path('second_blog/', views.second_blog, name='second_blog'),
    path('article=<article_id>/', views.aritcle_content),
    path('editor/', views.article_editor, name='article_editor')
]
