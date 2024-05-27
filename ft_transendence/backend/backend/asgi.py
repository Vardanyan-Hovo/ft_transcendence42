"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter , URLRouter
from chat import routing as chat_routing
from game import routing as game_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

application = ProtocolTypeRouter(
	{
		"http" : get_asgi_application() , 
		"websocket" : AuthMiddlewareStack(
			URLRouter(
                chat_routing.websocket_urlpatterns +
                game_routing.websocket_urlpatterns
			) 
		)
	}
)
