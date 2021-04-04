from __future__ import annotations

import asyncio
from json import dumps, loads
from typing import Any, Callable, Dict
from uuid import uuid4

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string

from main.models import WebinarSession


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


def get_chat_template(webinar_session: WebinarSession, event_id: str) -> str:
    webinar_session.login()
    event = webinar_session.get_event({'id': event_id})
    chat = webinar_session.get_chat(event)
    return render_to_string('components/widget/chat.html', {'chat': chat})


async def send_chat(consumer: ChatConsumer) -> None:
    template = await sync_to_async(get_chat_template)(consumer.webinar_session, consumer.event_id)
    await consumer.channel_layer.group_send(
        consumer.room,
        {
            'type': 'server_message',
            'message': {
                'event': 'update chat',
                'template': template
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
        data_event = {'id': self.event_id}
        event = self.webinar_session.get_event(data_event)
        if message['command'] == 'accept message':
            self.webinar_session.accept_message(message['message_id'], event)
        elif message['command'] == 'decline message':
            self.webinar_session.decline_message(message['message_id'], event)

    async def server_message(self, event: dict) -> None:
        await self.send(text_data=dumps(event['message']))
