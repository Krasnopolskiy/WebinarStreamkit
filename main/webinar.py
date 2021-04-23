from __future__ import annotations

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


class Webinar:
    """
    класс вебинара
    """
    class Routes:
        """
        так называемые маршруты (ссылки)

        :param STREAM: ссылка на сессию трансляции
        :param API: ссылка на API
        :param LOGIN: ссылка на страницу входа
        :param USER: ссылка на страницу пользователя
        :param PLANNED: ссылка на страницу запланированных событий вебинаров
        :param EVENT: ссылка на страницу события
        :param CHAT: ссылка на страницу чата
        :param ACCEPT_MESSAGE: ссылка на подтверждение сообщения
        :param ACCEPT_MESSAGE: ссылка на удаления сообщения
        """
        STREAM = 'https://events.webinar.ru/{user_id}/{event_id}/stream-new/{session_id}'
        API = 'https://events.webinar.ru/api/{route}'
        LOGIN = API.format(route='/login')
        USER = API.format(route='/user/{user_id}')
        PLANNED = API.format(route='/organizations/{organization_id}/eventsessions/list/planned')
        EVENT = API.format(route='/event/{event_id}')
        CHAT = API.format(route='/eventsessions/{session_id}/chat')
        ACCEPT_MESSAGE = API.format(route='/eventsessions/{session_id}/chat/messages/moderate')
        DELETE_MESSAGE = API.format(route='eventsessions/{session_id}/chat/messages/delete')

    class User:
        """
        класс пользователя

        :param attrs: аттрибуты пользователя
        """
        attrs = ['id', 'name', 'secondName', 'email']

        def __init__(self, data: Dict[str, Any] = {}, is_authenticated: bool = False) -> None:
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

        def __init__(self, data: Dict[str, Any]) -> None:
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

        def __init__(self, data: Dict[str, Any]) -> None:
            """
            Конструктор класса сообщения
            """
            self = Converter(self, self.attrs, data).convert()

        def serialize(self) -> Dict[str, Any]:
            """
            сериализация сообщения
            """
            return {attr: getattr(self, attr) for attr in self.attrs}

    class Chat:
        """
        класс чата
        """
        def __init__(self, messages: List[Dict]) -> None:
            """
            Конструктор класса чата
            """
            self.awaiting = []
            self.moderated = []
            for message in messages:
                message = Webinar.Message(message)
                [self.awaiting, self.moderated][message.isModerated].append(message)

    class Event:
        """
        класс события вединара

        :param attrs: аттрибуты события вединара

        """
        attrs = ['id', 'name', 'description', 'startsAt', 'endsAt']

        def __init__(self, user: Webinar.User, data: Dict[str, Any]) -> None:
            """
            Конструктор класса события вединара
            """
            self = Converter(self, self.attrs, data).convert()
            self.session_id = data['eventSessions'][0]['id']
            self.image = data['image']['url']
            self.url = Webinar.Routes.STREAM.format(
                user_id=user.id,
                event_id=self.id,
                session_id=self.session_id
            )
