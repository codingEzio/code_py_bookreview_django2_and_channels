from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from main import routing

application = ProtocolTypeRouter(
    {
        # http->django views is added by default
        "websocket": AuthMiddlewareStack(
            inner=URLRouter(routing.websocket_urlpatterns)
        )
    }
)
