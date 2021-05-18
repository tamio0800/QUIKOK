from django.conf.urls import include, url
from .import views
from django.urls import path

urlpatterns = [
    path('signupStudent/', views.create_a_student_user, name='signupStudent'),
    path('signupTeacher/', views.create_a_teacher_user, name='signupTeacher'),
    path('signin/', views.signin, name='to_signin'),
    path('logout/', views.logout, name='to_logout'),
    path('test/', views.test_connect_time),
    path('authCheck/', views.auth_check),
    path('returnTeacherProfileForOneselfViewing/', views.return_teacher_s_profile_for_oneself_viewing),
    path('returnTeacherProfileForPublicViewing/', views.return_teacher_s_profile_for_public_viewing),
    path('returnStudentProfileForOneselfViewing/', views.return_student_profile_for_oneself_viewing),
    path('returnStudentProfileForPublicViewing/', views.return_student_profile_for_public_viewing),
    path('editStudentProfile/', views.edit_student_profile),
    path('editTeacherProfile/', views.edit_teacher_profile),
    path('memberForgotPassword/', views.member_forgot_password),
    path('memberResetPassword/', views.member_reset_password),
    path('feedback/', views.feedback_view_function),
    path('getBankingInfomation/', views.get_banking_information),
    path('getStudentPublicReview/', views.get_student_public_review),
    path('getTeacherPublicReview/', views.get_teacher_public_review),
    path('memberChangePassword/', views.member_change_password),
]
