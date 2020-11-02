from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('lessons_main_page/', views.lessons_main_page),
    path('getLessonCardsForCommonUsers/', views.get_lesson_cards_for_common_users),
    path('getLessonCardsForTheTeacherWhoCreatedThem/', views.get_lesson_cards_for_the_teacher_who_created_them),
    path('returnLessonDetailsForTeacherWhoCreatedIt/', views.return_lesson_details_for_teacher_who_created_it),
    path('returnLessonDetailsForBrowsing/', views.return_lesson_details_for_browsing),
    path('createOrEditLesson/', views.test_create_or_edit_a_lesson),
    path('setLessonStatus/', views.set_lesson_s_status),
    path('addOrRemoveFavoriteLessons', views.add_or_remove_favorite_lessons),
    
    path('import_lesson/', views.import_lesson),
    path('createLesson/', views.lesson_manage),
    path('editLesson/', views.lesson_manage),
    path('showLessonDetail/', views.lesson_manage),
    path('fake_form/', views.fake_form),
    
]