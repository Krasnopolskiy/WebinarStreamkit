from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List


class Converter:
    """
    класс-конвертер
    """

    def __init__(self, object: Any, attrs: List[str], data: Dict[str, Any]) -> None:
        """
        конструктор класса

        :param object: объект
        :param data: данные
        :param attrs: аттрибуты, аргументы
        """
        self.object = object
        self.data = data
        self.attrs = attrs

    def convert(self) -> Any:
        """
        сама функция конвертирования
        """
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
    """
    класс вебинара
    """

    class User:
        """
        класс пользователя

        :param attrs: аттрибуты пользователя
        """
        attrs = ['id', 'name', 'secondName', 'email']

        def __init__(self, data: Dict = {}, is_authenticated: bool = False) -> None:
            """
            конструктор класса

            :param is_authenticated: флаг аутентификации пользователя
            :param memberships: членства пользователя (принадлежность организациям/группам)
            """
            self = Converter(self, self.attrs, data).convert()
            self.is_authenticated = is_authenticated
            self.memberships = [Webinar.Organization(membership['organization'])
                                for membership in data.get('memberships', [])]

    class Organization:
        """
        класс организации

        :param attrs: аттрибуты организации
        """
        attrs = ['id', 'name']

        def __init__(self, data: Dict) -> None:
            """
            Конструктор класса организации
            """
            self = Converter(self, self.attrs, data).convert()

    class Message:
        """
        класс сообщения

        :param attrs: аттрибуты сообщения
        """
        attrs = ['id', 'authorName', 'text', 'isModerated', 'createAt']

        def __init__(self, data: Dict) -> None:
            """
            Конструктор класса сообщения
            """
            self = Converter(self, self.attrs, data).convert()

        def serialize(self) -> Dict:
            """
            сериализация сообщения
            """
            return {attr: getattr(self, attr) for attr in self.attrs}

    class Chat:
        """
        класс чата
        """
        attrs = ['premoderation', 'show']

        def __init__(self, messages: List[Dict], settings: Dict) -> None:
            """
            Конструктор класса чата
            """
            self = Converter(self, self.attrs, settings).convert()
            self.awaiting = []
            self.moderated = []
            for message in messages:
                message = Webinar.Message(message)
                [self.awaiting, self.moderated][message.isModerated].append(message)
            self.awaiting.reverse()
            self.moderated.reverse()

    class Event:
        """
        класс события вединара

        :param attrs: аттрибуты события вединара

        """
        attrs = ['id', 'name', 'description', 'startsAt', 'endsAt']

        def __init__(self, user_id: int, data: Dict) -> None:
            """
            Конструктор класса события вединара
            """
            self = Converter(self, self.attrs, data).convert()
            self.session_id = data['eventSessions'][0]['id']
            self.status = data['eventSessions'][0]['status']
            self.image = data['image']['url']
            self.url = BaseRouter.STREAM.value.format(
                user_id=user_id,
                event_id=self.id,
                session_id=self.session_id
            )

    class Error:
        attrs = ['code', 'message']

        def __init__(self, data: Dict) -> None:
            self = Converter(self, self.attrs, data).convert()
            self.message = f'Webinar: {self.message}'
