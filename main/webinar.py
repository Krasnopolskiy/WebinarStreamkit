from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List


class Converter:
    def __init__(self, object: Any, attrs: List[str], data: Dict[str, Any]) -> None:
        self.object = object
        self.data = data
        self.attrs = attrs

    def convert(self) -> Any:
        for attr in set(self.data) & set(self.attrs):
            setattr(self.object, attr, self.data[attr])
        return self.object


class BaseRouter(Enum):
    EVENTS = 'https://events.webinar.ru/{route}'
    STREAM = EVENTS.format(route='{user_id}/{event_id}/stream-new/{session_id}')
    API = EVENTS.format(route='api/{route}')


class UserRouter(Enum):
    LOGIN = BaseRouter.API.value.format(route='login')
    INFO = BaseRouter.API.value.format(route='user/{user_id}')


class EventRouter(Enum):
    PLANNED = BaseRouter.API.value.format(route='organizations/{organization_id}/eventsessions/list/planned')
    INFO = BaseRouter.API.value.format(route='event/{event_id}')
    START = BaseRouter.API.value.format(route='eventsession/{session_id}/start')
    STOP = BaseRouter.API.value.format(route='eventsession/{session_id}/stop')


class MessageRouter(Enum):
    CHAT = BaseRouter.API.value.format(route='eventsessions/{session_id}/chat')
    ACCEPT = BaseRouter.API.value.format(route='eventsessions/{session_id}/chat/messages/moderate')
    DELETE = BaseRouter.API.value.format(route='eventsessions/{session_id}/chat/messages/delete')
    SETTINGS = BaseRouter.API.value.format(route='eventsessions/{session_id}/chat/settings')


class Webinar:
    class User:
        attrs = ['id', 'name', 'secondName', 'email']

        def __init__(self, data: Dict[str, Any] = {}, is_authenticated: bool = False) -> None:
            self = Converter(self, self.attrs, data).convert()
            self.is_authenticated = is_authenticated
            self.memberships = [Webinar.Organization(membership['organization'])
                                for membership in data.get('memberships', [])]

    class Organization:
        attrs = ['id', 'name']

        def __init__(self, data: Dict[str, Any]) -> None:
            self = Converter(self, self.attrs, data).convert()

    class Message:
        attrs = ['id', 'authorName', 'text', 'isModerated', 'createAt']

        def __init__(self, data: Dict[str, Any]) -> None:
            self = Converter(self, self.attrs, data).convert()

        def serialize(self) -> Dict[str, Any]:
            return {attr: getattr(self, attr) for attr in self.attrs}

    class Chat:
        def __init__(self, messages: List[Dict]) -> None:
            self.awaiting = []
            self.moderated = []
            for message in messages:
                message = Webinar.Message(message)
                [self.awaiting, self.moderated][message.isModerated].append(message)
            self.awaiting.reverse()
            self.moderated.reverse()

    class Event:
        attrs = ['id', 'name', 'description', 'startsAt', 'endsAt']

        def __init__(self, user_id: int, data: Dict[str, Any]) -> None:
            self = Converter(self, self.attrs, data).convert()
            self.session_id = data['eventSessions'][0]['id']
            self.status = data['eventSessions'][0]['status']
            self.image = data['image']['url']
            self.url = BaseRouter.STREAM.value.format(
                user_id=user_id,
                event_id=self.id,
                session_id=self.session_id
            )
