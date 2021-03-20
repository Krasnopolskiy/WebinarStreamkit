import json
from typing import Dict
from requests import Session

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import requests


class WebinarApi:
    URL = 'https://events.webinar.ru/api'

    def __init__(self, user) -> None:
        self.session = Session()
        self.login(user.webinar_email, user.webinar_password)

    def login(self, email, password) -> None:
        self.session.post(WebinarApi.URL + '/login', data={'email': email, 'password': password})

    def get_chat(self, chat_id) -> Dict:
        data = self.session.get(WebinarApi.URL + f'/eventsessions/{chat_id}/chat').text
        return json.loads(data)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.chat_id = self.scope['url_route']['kwargs']['id']
        self.chat = str(self.chat_id)
        self.api = await sync_to_async(WebinarApi)(self.scope['user'])

        await self.channel_layer.group_add(
            self.chat,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code) -> None:
        await self.channel_layer.group_discard(
            self.chat,
            self.channel_name
        )

    async def receive(self, text_data: str) -> None:
        commands = {
            'get_chat': {
                'function': self.api.get_chat,
                'params': self.chat
            }
        }
        command = text_data
        message = await sync_to_async(commands[command]['function'])(commands[command]['params'])
        await self.channel_layer.group_send(
            self.chat,
            {
                'type': 'server_message',
                'message': message
            }
        )

    async def server_message(self, event: dict) -> None:
        await self.send(text_data=json.dumps(event['message']))
