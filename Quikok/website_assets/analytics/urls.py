from analytics import views
from django.urls import path

urlpatterns = [
    path('quikok_dashboard/', views.quikok_dashboard, name='quikok_dashboard'),
]