from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import pong.routing

# chat is not working anymore but not used
application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(pong.routing.websocket_urlpatterns)
        ),
    }
)