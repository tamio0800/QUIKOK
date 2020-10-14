from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('lessons_main_page/', views.lessons_main_page),
    path('recommendList/', views.get_lesson_card),
    path('import_lesson/', views.import_lesson),
    path('createlesson/', views.lesson_manage),
    path('testCreateLesson/', views.lesson_manage),
    path('editLesson/', views.lesson_manage),
    path('showLessonDetail/', views.lesson_manage),
    
]