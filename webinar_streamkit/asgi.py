"""
ASGI config for webinar_streamkit project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webinar_streamkit.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application



from . import urls

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            urls.websocket_urlpatterns
        )
    )
})
