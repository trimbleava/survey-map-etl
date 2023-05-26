# asgi.py
import os

#
# SessionMiddleware requires CookieMiddleware to function. 
# For convenience, these are also provided as a combined callable 
# called SessionMiddlewareStack that includes both.
# The AuthMiddleware in Channels supports standard Django authentication, 
# where the user details are stored in the session. It allows read-only 
# access to a user object in the scope.
# AuthMiddleware requires SessionMiddleware to function, which itself requires 
# CookieMiddleware. For convenience, these are also provided as a combined 
# callable called AuthMiddlewareStack that includes all three.
#
from channels.auth import AuthMiddlewareStack
#
# Often, the set of domains you want to restrict to is the same as the 
# Django ALLOWED_HOSTS setting, which performs a similar security check 
# for the Host header, and so AllowedHostsOriginValidator lets you use 
# this setting without having to re-declare the list:
#
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "heath_lsa.setting_dir.prod_settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# app modules
from tenants.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
