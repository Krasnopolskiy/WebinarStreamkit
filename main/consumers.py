from __future__ import annotations

import asyncio
from json import dumps, loads
from typing import Any, Callable, Dict
from uuid import uuid4

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from main.models import WebinarSession
from main.webinar import Webinar


class Timer:
    def __init__(self, timeout: float, callback: Callable, *args: Any, **kwargs: Dict[str, Any]) -> None:
        self.timeout = timeout
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.task = asyncio.Future

    def enable(self) -> None:
        self.enabled = True
        self.task = asyncio.ensure_future(self.job())

    async def job(self) -> None:
        while self.enabled:
            await self.callback(*self.args, **self.kwargs)
            await asyncio.sleep(self.timeout)

    def cancel(self):
        self.enabled = False
        self.task.cancel()


def get_chat(webinar_session: WebinarSession, event_id: str) -> Webinar.Chat:
    webinar_session.login()
    event = webinar_session.get_event({'id': event_id})
    return webinar_session.get_chat(event)


async def send_chat(consumer: ChatConsumer) -> None:
    chat = await sync_to_async(get_chat)(consumer.webinar_session, consumer.event_id)
    await consumer.channel_layer.group_send(
        consumer.room,
        {
            'type': 'server_message',
            'message': {
                'event': 'update_chat',
                'chat': await sync_to_async(chat.serialize)()
            }
        }
    )


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room = f'client_{self.event_id}_{uuid4()}'

        user_id = self.scope['user'].id
        self.webinar_session = await sync_to_async(WebinarSession.objects.get)(user=user_id)
        self.timer = Timer(1, send_chat, self)
        self.timer.enable()

        await self.channel_layer.group_add(
            self.room,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(
            self.room,
            self.channel_name
        )

    async def receive(self, text_data: str) -> None:
        message = loads(text_data)

    async def server_message(self, event: dict) -> None:
        await self.send(text_data=dumps(event['message']))
