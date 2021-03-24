from typing import Any, Dict, List


class WebinarRoutes:
    API = 'https://events.webinar.ru/api/{route}'
    LOGIN = API.format(route='/login')
    PLANNED = API.format(route='/organizations/{organization_id}/eventsessions/list/planned')
    EVENT = API.format(route='/event/{event_id}')
    CHAT = API.format(route='/eventsessions/{session_id}/chat')


class WebinarMessage:
    def __init__(self, **data: Any) -> None:
        attrs = ['id', 'authorName', 'text', 'isModerated']
        for attr in set(data) & set(attrs):
            setattr(self, attr, data[attr])


class WebinarChat:
    def __init__(self, messages: List[Dict]) -> None:
        self.messages = [WebinarMessage(**message) for message in messages]

    def get_moderated(self) -> List[WebinarMessage]:
        return [message for message in self.messages if message.isModerated]

    def get_awaiting(self) -> List[WebinarMessage]:
        return [message for message in self.messages if not message.isModerated]


class WebinarEvent:
    def __init__(self, **data: Any) -> None:
        attrs = ['id', 'name', 'description', 'startsAt', 'endsAt']
        for attr in set(data) & set(attrs):
            setattr(self, attr, data[attr])
        self.session_id = data['eventSessions'][0]['id']
