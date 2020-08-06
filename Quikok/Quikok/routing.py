from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import chatroom.routing

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chatroom.routing.websocket_urlpatterns
        )
    ),
})
