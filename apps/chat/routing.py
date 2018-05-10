from django.urls import path

from apps.chat.consumers import ChatConsumer

urlpatterns = [
    path("ws/chat/<str:room_name>", ChatConsumer),
]