from json import loads
from typing import Any, Dict, List
from django.contrib.auth.models import AbstractUser
from django.db import models
from requests import Session

from main.webinar import Webinar


class WebinarSession(models.Model):
    email = models.EmailField(max_length=255, default='')
    password = models.CharField(max_length=255, default='')
    active = models.BooleanField(default=False)

    session = Session()
    webinar_user = Webinar.User()

    def login(self) -> None:
        route = Webinar.Routes.LOGIN
        payload = {'email': self.email, 'password': self.password}
        response = loads(self.session.post(route, data=payload).text)
        if 'error' not in response:
            self.active = True
            data = loads(self.session.get(route).text)
            self.webinar_user = self.get_user(data)

    def get_user(self, user: Dict[str, Any]) -> Webinar.User:
        route = Webinar.Routes.USER.format(user_id=user['id'])
        data = loads(self.session.get(route).text)
        return Webinar.User(**data)

    def get_chat(self, event: Webinar.Event) -> Webinar.Chat:
        route = Webinar.Routes.CHAT.format(session_id=event.session_id)
        data = loads(self.session.get(route).text)
        return Webinar.Chat(data)

    def get_event(self, event: Dict[str, Any]) -> Webinar.Event:
        event_id = event.get('eventId', event['id'])
        route = Webinar.Routes.EVENT.format(event_id=event_id)
        data = loads(self.session.get(route).text)
        if 'error' not in data:
            return Webinar.Event(self.webinar_user, **data)

    def get_schedule(self) -> List[Webinar.Event]:
        schedule = list()
        for organisation in self.webinar_user.memberships:
            route = Webinar.Routes.PLANNED.format(organization_id=organisation.id)
            events = loads(self.session.get(route).text)
            schedule += list(filter(
                lambda event: event is not None,
                [self.get_event(event) for event in events]
            ))
        return schedule

    def accept_message(self, message_id: int, event: Webinar.Event) -> None:
        request_body = {'isModerated': 'true', 'messageIds[0]': message_id}
        route = Webinar.Routes.ACCEPT_MESSAGE.format(session_id=event.session_id)
        response = loads(self.session.put(route, data=request_body).text)
        print(response)


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars', default='avatar.svg')
    webinar_session = models.OneToOneField(WebinarSession, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        if self.id is None:
            self.webinar_session = WebinarSession.objects.create()
        super(User, self).save(*args, **kwargs)
