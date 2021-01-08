from .import views
from django.urls import path

urlpatterns = [
    path('storageOrder/', views.storage_order),
    path('read_email/', views.view_email_new_order_remind),
    path('confirm_lesson_order_payment/', views.confirm_lesson_order_payment_page),
    path('getLessonSalesHistory/', views.get_lesson_sales_history),
    #path('create_lesson_order_minute/', views.create_student_purchase_remain_minutes)
]