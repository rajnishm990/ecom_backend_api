"""
ASGI config for ecommerce_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from orders.routing import websocket_urlpatterns


from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')

application = get_asgi_application()

# This router handles both HTTP and WebSocket connections
application = ProtocolTypeRouter({
    'http': django_asgi_app,  # Normal HTTP requests
    'websocket': AuthMiddlewareStack(  # WebSocket connections with auth
        URLRouter(
            websocket_urlpatterns
        )
    ),
})