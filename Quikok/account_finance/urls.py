from .import views
from django.urls import path

urlpatterns = [
    path('storageOrder/', views.storage_order),
    path('studentOrderHistory/', views.student_order_history),
    path('studentEditOrder/', views.student_edit_order),
    path('read_email/', views.view_email_new_order_remind),
    path('getLessonSalesHistory/', views.get_lesson_sales_history),
    path('withdrawQPoints/', views.withdraw_q_points),
    path('getQPointsWithdrawalHistory/', views.get_q_points_wtihdrawal_history),

    #path('confirm_lesson_order_payment/', views.confirm_lesson_order_payment_page),
    #path('create_lesson_order_minute/', views.create_student_purchase_remain_minutes)
]