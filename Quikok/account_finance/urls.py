from .import views
from django.urls import path

urlpatterns = [
    path('storageOrder/', views.storage_order),
    path('studentOrderHistory/', views.student_order_history),
    path('read_email/', views.view_email_new_order_remind),
    #path('confirm_lesson_order_payment/', views.confirm_lesson_order_payment_page),
    #path('create_lesson_order_minute/', views.create_student_purchase_remain_minutes)
]