"""
ASGI config for game_verse project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_verse.settings')
application = get_asgi_application()

from channels.auth import AuthMiddlewareStack
import main.routing

application = ProtocolTypeRouter(
  {
    'http':application,
    'websocket':AuthMiddlewareStack(
      URLRouter(
        main.routing.websocket_urlpatterns
      )
    )
  }
)
