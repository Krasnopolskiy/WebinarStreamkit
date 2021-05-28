"""
Consumers для работы с сокетами
"""

from __future__ import annotations

import asyncio
from enum import Enum
from json import dumps, loads
from typing import Any, Callable, Dict
from uuid import uuid4

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string

from main.discord import DiscordClient
from main.models import DiscordHistory, User, WebinarSession
from main.webinar import Webinar


class ChatMode(Enum):
    MODERATED = 'moderated'
    AWAITING = 'awaiting'


class Timer:
    """
    Класс таймера
    """

    def __init__(self, timeout: float, callback: Callable, *args: Any, **kwargs: Dict) -> None:
        """
        Конструктоор
        :param timeout: Сколько секунд между действиями
        :param callback: Функция, которая будет вызываться каждые timeout секунд
        """
        self.timeout = timeout
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.enabled = False
        self.task = asyncio.Future

    def enable(self) -> None:
        self.enabled = True
        self.task = asyncio.ensure_future(self.job())

    async def job(self) -> None:
        while self.enabled:
            try:
                await self.callback(*self.args, **self.kwargs)
            except Exception as error:
                await send_error(*self.args, **self.kwargs)
            await asyncio.sleep(self.timeout)

    def cancel(self):
        """
        Функция отключения таймера
        """
        self.enabled = False
        self.task.cancel()


def get_chat_template(webinar_session: WebinarSession, event_id: int, mode: ChatMode) -> str:
    event = webinar_session.get_event(event_id)
    chat = webinar_session.get_chat(event.session_id)
    return render_to_string(f'components/widget/{mode.value}.html', {'chat': chat})


async def send_chat(consumer: ChatConsumer) -> None:
    """
    Метод отправки чата
    """
    template = await sync_to_async(get_chat_template)(
        consumer.webinar_session,
        consumer.event_id,
        consumer.mode
    )

    await consumer.channel_layer.group_send(
        consumer.room,
        {
            'type': 'server_message',
            'message': {
                'event': 'update messages',
                'template': template
            }
        }
    )


def get_event_settings(webinar_session: WebinarSession, event_id: int) -> Webinar.Chat:
    """
    Получение настроек о событии
    """
    event = webinar_session.get_event(event_id)
    chat = webinar_session.get_chat(event.session_id)
    history = DiscordHistory.objects.get(event_id=event_id)
    return {
        'status': event.status,
        'premoderation': chat.premoderation == 'True',
        'broadcast': history.active
    }


async def send_settings(consumer: ControlConsumer) -> None:
    settings = await sync_to_async(get_event_settings)(
        consumer.webinar_session,
        consumer.event_id
    )

    await consumer.channel_layer.group_send(
        consumer.room,
        {
            'type': 'server_message',
            'message': {
                'event': 'update settings',
                'settings': settings
            }
        }
    )


async def send_error(consumer: BaseConsumer) -> None:
    await consumer.channel_layer.group_send(
        consumer.room,
        {
            'type': 'server_message',
            'message': {
                'event': 'error'
            }
        }
    )


class BaseConsumer(AsyncWebsocketConsumer):

    async def connect(self) -> None:
        """
        Метод, срабатывающий после подключения по websockets
        """
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room = f'client_{self.event_id}_{uuid4()}'
        user_id = self.scope['user'].id
        self.user = await sync_to_async(User.objects.get)(id=user_id)
        self.webinar_session = await sync_to_async(WebinarSession.objects.get)(user=user_id)

        await self.channel_layer.group_add(
            self.room,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code: int) -> None:
        self.timer.cancel()
        await self.channel_layer.group_discard(
            self.room,
            self.channel_name
        )

    async def receive(self, text_data: str) -> None:
        """
        Метод принятия сообщений по websockets
        """
        message = loads(text_data)
        event = await sync_to_async(self.webinar_session.get_event)(self.event_id)
        if message['command'] in self.commands:
            await self.commands[message['command']](event.session_id, **message['params'])

    async def server_message(self, event: dict) -> None:
        await self.send(text_data=dumps(event['message']))


class ChatConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        """
        Конструктор класса
        """
        super(ChatConsumer, self).__init__(*args, **kwargs)
        self.mode = ChatMode.MODERATED
        self.commands = {}
        self.timer = Timer(1, send_chat, self)

    async def connect(self) -> None:
        """
        Метод, срабатывающий после подключения по websockets
        """
        await super().connect()

        self.commands['delete message'] = sync_to_async(self.webinar_session.delete_message)
        self.timer.enable()


class AwaitingMessagesConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        """
        Конструктор класса
        """
        super().__init__(*args, **kwargs)
        self.timer = Timer(1, send_chat, self)
        self.mode = ChatMode.AWAITING
        self.commands = {}

    async def connect(self) -> None:
        """
        Метод, срабатывающий после подключения по websockets
        """
        await super().connect()
        self.commands['accept message'] = sync_to_async(self.webinar_session.accept_message),
        self.commands['delete message'] = sync_to_async(self.webinar_session.delete_message),
        self.timer.enable()


class ControlConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        """
        Конструктор класса
        """
        super().__init__(*args, **kwargs)
        self.timer = Timer(1, send_settings, self)
        self.commands = {}

    async def connect(self) -> None:
        """
        Метод, срабатывающий после подключения по websockets
        """
        await super().connect()

        self.discord_client = DiscordClient(self.webinar_session, self.event_id)
        await sync_to_async(self.discord_client.get_history_instance)()

        self.commands['update settings'] = sync_to_async(self.webinar_session.update_settings)
        self.commands['update fontsize'] = sync_to_async(self.user.update_fontsize)
        self.commands['update broadcast settings'] = sync_to_async(self.discord_client.history.update_settings)
        self.commands['start'] = sync_to_async(self.webinar_session.start)
        self.commands['stop'] = sync_to_async(self.webinar_session.stop)
        self.timer.enable()

        self.discord_timer = Timer(1, sync_to_async(self.discord_client.process))
        self.discord_timer.enable()

    async def disconnect(self, close_code: int) -> None:
        self.discord_timer.cancel()
        return await super().disconnect(close_code)
