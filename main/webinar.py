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

    class User:
        def __init__(self, **data: Any) -> None:
            attrs = ['id', 'name', 'secondName']
            self = Converter(self, attrs, **data).convert()
            self.memberships = [Webinar.Organization(**membership['organization'])
                                for membership in data.get('memberships', [])]

    class Organization:
        def __init__(self, **data: Any) -> None:
            attrs = ['id', 'name']
            self = Converter(self, attrs, **data).convert()

    class Message:
        def __init__(self, **data: Any) -> None:
            attrs = ['id', 'authorName', 'text', 'isModerated', 'createAt']
            self = Converter(self, attrs, **data).convert()

    class Chat:
        def __init__(self, messages: List[Dict]) -> None:
            self.messages = [Webinar.Message(**message) for message in messages]

        def get_moderated(self) -> List[Webinar.Message]:
            return [message for message in self.messages if message.isModerated]

        def get_awaiting(self) -> List[Webinar.Message]:
            return [message for message in self.messages if not message.isModerated]

    class Event:
        def __init__(self, user: Webinar.User, **data: Any) -> None:
            attrs = ['id', 'name', 'description', 'startsAt', 'endsAt']
            self = Converter(self, attrs, **data).convert()
            self.session_id = data['eventSessions'][0]['id']
            self.image = data['image']['url']
            self.url = Webinar.Routes.STREAM.format(
                user_id=user.id,
                event_id=self.id,
                session_id=self.session_id
            )
