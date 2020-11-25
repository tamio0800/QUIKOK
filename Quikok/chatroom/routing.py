from django.urls import path

from . import consumers
websocket_urlpatterns = [
    path('ws/chat/<str:room_url>/', consumers.ChatConsumer),
    path('ws/chat/<str:system_room_url>/', consumers.ChatConsumer),
]

# url.py for websocket
