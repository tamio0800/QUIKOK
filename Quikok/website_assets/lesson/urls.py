from lesson import views
from django.urls import path

urlpatterns = [
    path('lessons_main_page/', views.lessons_main_page),
    path('getLessonCardsForCommonUsers/', views.get_lesson_cards_for_common_users),
    path('getLessonCardsForTheTeacherWhoCreatedThem/', views.get_lesson_cards_for_the_teacher_who_created_them),
    path('returnLessonDetailsForTeacherWhoCreatedIt/', views.return_lesson_details_for_teacher_who_created_it),
    path('returnLessonDetailsForBrowsing/', views.return_lesson_details_for_browsing),
    path('createOrEditLesson/', views.create_or_edit_a_lesson),
    path('beforeSigningUpCreateOrEditLesson/', views.before_signing_up_create_or_edit_a_lesson),
    path('setLessonStatus/', views.set_lesson_s_status),
    path('addOrRemoveFavoriteLessons/', views.add_or_remove_favorite_lessons),
    path('getALLFilteredKeysAndValues/', views.get_all_filtered_keys_and_values),
    path('import_lesson/', views.import_lesson),
    #path('createLesson/', views.lesson_manage),
    #path('editLesson/', views.lesson_manage),
    path('showLessonDetail/', views.lesson_manage),
    path('fake_form/', views.fake_form),
    path('getLessonSpecificAvailableTime/', views.get_lesson_specific_available_time),
    path('bookingLessons/', views.booking_lessons),
    path('changingLessonBookingStatus/', views.changing_lesson_booking_status),
    path('getStudentsAvailableRemainingMinutes/', views.get_student_s_available_remaining_minutes),
    path('getTeachersBookingHistory/', views.get_teacher_s_booking_history),
    path('getStudentsBookingHistory/', views.get_student_s_booking_history),
    path('lessonCompletedNotificationFromTeacher/', views.lesson_completed_notification_from_teacher),
    path('lessonCompletedConfirmationFromStudent/', views.lesson_completed_confirmation_from_student),
    path('teacherWriteStudentReviews/', views.teacher_write_student_reviews),
    path('studentWriteTeacherReviews/', views.student_write_teacher_reviews),
    path('readReviewsOfCertainLessons/', views.read_reviews_of_certain_lessons)
]