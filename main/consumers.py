import logging

from django.shortcuts import get_object_or_404
import aioredis
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from . import models


REDIS_ADDR = "redis//localhost"
logger = logging.getLogger(name="__name__")


class ChatConsumer(AsyncJsonWebsocketConsumer):
    EMPLOYEE = 2
    CLIENT = 1

    def get_user_type(self, user, order_id):
        order = get_object_or_404(models.Order, pk=order_id)

        if user.is_employee:
            order.last_spoken_to = user.order.save()
            return ChatConsumer.EMPLOYEE
        elif order.user == user:
            return ChatConsumer.CLIENT
        else:
            return None

    async def connect(self):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.room_group_name = f"customer-service_{self.order_id}"
        authorized = False

        if self.scope["user"].is_anonymous:
            await self.close()

        user_type = await database_sync_to_async(self.get_user_type)(
            self.scope["user"], self.order_id
        )

        if user_type == ChatConsumer.EMPLOYEE:
            logger.info(
                f"Opening chat stream for employee {self.scope['user']}"
            )
            authorized = True
        elif user_type == ChatConsumer.CLIENT:
            logger.info(f"Opening chat stream for client {self.scope['user']}")
            authorized = True
        else:
            logger.info(f"Unauthorized connection from {self.scope['user']}")
            await self.close()

        if authorized:
            self.redis_conn = await aioredis.create_redis(address=REDIS_ADDR)

            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_join",
                    "username": self.scope["user"].get_full_name(),
                },
            )

    async def disconnect(self):
        if not self.scope["user"].is_anonymous:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_leave",
                    "username": self.scope["user"].get_full_name(),
                },
            )
            logger.info(f"Closing chat stream for user {self.scope['user']}")
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive_json(self, content):
        cont_type = content.get("type")

        if cont_type == "message":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "username": self.scope["user"].get_full_name(),
                    "message": content["message"],
                },
            )
        elif cont_type == "heartbeat":
            await self.redis_conn.setex(
                key=f"{self.room_group_name}_{self.scope['user'].email}",
                seconds=10,
                value="1",  # a dummy value
            )

    async def chat_message(self, event):
        await self.send_json(content=event)

    async def chat_join(self, event):
        await self.send_json(content=event)

    async def chat_leave(self, event):
        await self.send_json(content=event)
