from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('lessons_main_page/', views.lessons_main_page),
    path('recommendList/', views.get_lesson_card),
    path('import_lesson/', views.import_lesson),
    path('createlesson/', views.lesson_manage),
    path('test_create_lesson/', views.lesson_manage),
    path('editlesson/', views.lesson_manage),
    path('show_lesson_detail/', views.lesson_manage),
    
]