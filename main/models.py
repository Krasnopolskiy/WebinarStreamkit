from json import loads
from typing import Dict, List

from django.contrib.auth.models import AbstractUser
from django.db import models
from requests import Session

from main.webinar import WebinarChat, WebinarEvent, WebinarRoutes


class WebinarSession(models.Model):
    email = models.EmailField(max_length=255, default='')
    password = models.CharField(max_length=255, default='')
    nickname = models.CharField(max_length=255, default='')

    user_id = models.PositiveIntegerField(null=True)
    organization_id = models.PositiveIntegerField(null=True)
    active = models.BooleanField(default=False)

    session = Session()

    def login(self) -> None:
        route = WebinarRoutes.LOGIN
        payload = {'email': self.email, 'password': self.password}
        response = loads(self.session.post(route, data=payload).text)
        if 'error' not in response:
            data = loads(self.session.get(route).text)
            self.active = True
            self.user_id = data['id']
            self.organization_id = data['memberships'][0]['organization']['id']

    def get_chat(self, event: WebinarEvent) -> WebinarChat:
        route = WebinarRoutes.CHAT.format(session_id=event.session_id)
        data = loads(self.session.get(route).text)
        return WebinarChat(data)

    def get_event(self, event: Dict) -> WebinarEvent:
        event_id = event.get('eventId', event['id'])
        route = WebinarRoutes.EVENT.format(event_id=event_id)
        data = loads(self.session.get(route).text)
        if 'error' not in data:
            return WebinarEvent(**data)

    def get_schedule(self) -> List[WebinarEvent]:
        route = WebinarRoutes.PLANNED.format(organization_id=self.organization_id)
        events = loads(self.session.get(route).text)
        return list(filter(
            lambda event: event is not None,
            [self.get_event(event) for event in events]
        ))

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars', default='avatar.svg')
    webinar_session = models.OneToOneField(WebinarSession, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        if self.id is None:
            self.webinar_session = WebinarSession.objects.create()
        super(User, self).save(*args, **kwargs)
