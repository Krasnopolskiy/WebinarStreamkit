from __future__ import annotations

from typing import Any, Dict, List

from django.db import router


class Converter:
    def __init__(self, object: Any, attrs: List[str], data: Dict[str, Any]) -> None:
        self.object = object
        self.data = data
        self.attrs = attrs

    def convert(self) -> Any:
        for attr in set(self.data) & set(self.attrs):
            setattr(self.object, attr, self.data[attr])
        return self.object


class Webinar:
    class Routes:
        DOMAIN = 'https://events.webinar.ru/{url}'
        STREAM = DOMAIN.format(url='{user_id}/{event_id}/stream-new/{session_id}')
        API = DOMAIN.format(url='api/{route}')
        LOGIN = API.format(route='login')
        USER = API.format(route='user/{user_id}')
        PLANNED = API.format(route='organizations/{organization_id}/eventsessions/list/planned')
        EVENT = API.format(route='event/{event_id}')
        CHAT = API.format(route='eventsessions/{session_id}/chat')
        ACCEPT_MESSAGE = API.format(route='eventsessions/{session_id}/chat/messages/moderate')
        DELETE_MESSAGE = API.format(route='eventsessions/{session_id}/chat/messages/delete')
        SETTINGS = API.format(route='eventsessions/{session_id}/chat/settings')
        START = API.format(route='eventsession/{session_id}/start')
        STOP = API.format(route='eventsession/{session_id}/stop')

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
            self.url = Webinar.Routes.STREAM.format(
                user_id=user_id,
                event_id=self.id,
                session_id=self.session_id
            )
