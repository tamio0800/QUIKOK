from .import views
from django.urls import path

urlpatterns = [
    path('storageOrder/', views.storage_order),
]