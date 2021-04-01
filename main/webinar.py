from __future__ import annotations

from typing import Any, Dict, List


class Converter:
    def __init__(self, object: Any, attrs: List[str], **data) -> None:
        self.object = object
        self.data = data
        self.attrs = attrs

    def convert(self) -> Any:
        for attr in set(self.data) & set(self.attrs):
            setattr(self.object, attr, self.data[attr])
        return self.object


class Webinar:
    class Routes:
        STREAM = 'https://events.webinar.ru/{user_id}/{event_id}/stream-new/{session_id}'
        API = 'https://events.webinar.ru/api/{route}'
        LOGIN = API.format(route='/login')
        USER = API.format(route='/user/{user_id}')
        PLANNED = API.format(route='/organizations/{organization_id}/eventsessions/list/planned')
        EVENT = API.format(route='/event/{event_id}')
        CHAT = API.format(route='/eventsessions/{session_id}/chat')
        ACCEPT_MESSAGE = API.format(route='/eventsessions/<session_id>/chat/messages/moderate')

    class User:
        attrs = ['id', 'name', 'secondName']

        def __init__(self, **data: Any) -> None:
            self = Converter(self, self.attrs, **data).convert()
            self.memberships = [Webinar.Organization(**membership['organization'])
                                for membership in data.get('memberships', [])]

    class Organization:
        attrs = ['id', 'name']

        def __init__(self, **data: Any) -> None:
            self = Converter(self, self.attrs, **data).convert()

    class Message:
        attrs = ['id', 'authorName', 'text', 'isModerated', 'createAt']

        def __init__(self, **data: Any) -> None:
            self = Converter(self, self.attrs, **data).convert()

        def serialize(self) -> Dict[str, Any]:
            return {attr: getattr(self, attr) for attr in self.attrs}

    class Chat:
        def __init__(self, messages: List[Dict]) -> None:
            self.moderated = [Webinar.Message(**message) for message in messages if message['isModerated']]
            self.awaiting = [Webinar.Message(**message) for message in messages if not message['isModerated']]

        def serialize(self) -> List[Webinar.Message]:
            return {
                'moderated': [message.serialize() for message in self.moderated],
                'awaiting': [message.serialize() for message in self.awaiting]
            }

    class Event:
        attrs = ['id', 'name', 'description', 'startsAt', 'endsAt']

        def __init__(self, user: Webinar.User, **data: Any) -> None:
            self = Converter(self, self.attrs, **data).convert()
            self.session_id = data['eventSessions'][0]['id']
            self.image = data['image']['url']
            self.url = Webinar.Routes.STREAM.format(
                user_id=user.id,
                event_id=self.id,
                session_id=self.session_id
            )
