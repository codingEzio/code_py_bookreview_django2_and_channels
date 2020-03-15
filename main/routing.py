from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path(
        route="ws/customer-service/<int:order_id>/",
        view=consumers.ChatConsumer,
    )
]
