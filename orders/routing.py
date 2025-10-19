from django.urls import re_path
from . import consumers

# WebSocket URL patterns
websocket_urlpatterns = [
    re_path(r'ws/orders/notifications/$', consumers.OrderNotificationConsumer.as_asgi()),
]