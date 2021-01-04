from .import views
from django.urls import path

urlpatterns = [
    path('storageOrder/', views.storage_order),
    path('read_email/', views.view_email_new_order_remind),
    path('confirm_lesson_order_payment/', views.confirm_lesson_order_payment_page)
]