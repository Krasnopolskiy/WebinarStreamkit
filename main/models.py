from http.cookiejar import Cookie
from json import loads
from time import time
from typing import Any, Dict, List, Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from requests import Session

from main.webinar import Webinar


class WebinarSession(models.Model):
    email = models.EmailField(max_length=255, default='')
    password = models.CharField(max_length=255, default='')
    session = Session()
    webinar_user = Webinar.User()

    def get_session_cookie(self) -> Optional[Cookie]:
        for cookie in self.session.cookies:
            if cookie.name == 'sessionId':
                return cookie

    def validate_session(self) -> bool:
        cookie = self.get_session_cookie()
        return cookie is not None \
            and time() <= cookie.expires \
            and self.webinar_user.is_authenticated

    def login_user(self) -> Optional[Dict]:
        route = Webinar.Routes.LOGIN
        payload = {'email': self.email, 'password': self.password}
        response = loads(self.session.post(route, data=payload).text)
        if 'error' in response:
            return response
        data = loads(self.session.get(route, data=payload).text)
        route = Webinar.Routes.USER.format(user_id=data['id'])
        data = loads(self.session.get(route).text)
        self.webinar_user = Webinar.User(data, True)
        self.save()
    
    def ensure_session(self) -> None:
        if not self.validate_session():
            err = self.login_user()
            if err is not None:
                raise Exception
    
    def get_user(self) -> Webinar.User:
        self.ensure_session()
        return self.webinar_user

    def get_schedule(self) -> List[Webinar.Event]:
        self.ensure_session()
        schedule = list()
        for organisation in self.webinar_user.memberships:
            route = Webinar.Routes.PLANNED.format(organization_id=organisation.id)
            events = loads(self.session.get(route).text)
            schedule += list(filter(
                lambda event: event is not None,
                [self.get_event(event) for event in events]
            ))
        return schedule

    def get_event(self, event: Dict[str, Any]) -> Webinar.Event:
        self.ensure_session()
        event_id = event.get('eventId', event['id'])
        route = Webinar.Routes.EVENT.format(event_id=event_id)
        data = loads(self.session.get(route).text)
        if 'error' not in data:
            return Webinar.Event(self.webinar_user, data)

    def get_chat(self, event: Webinar.Event) -> Webinar.Chat:
        self.ensure_session()
        route = Webinar.Routes.CHAT.format(session_id=event.session_id)
        data = loads(self.session.get(route).text)
        return Webinar.Chat(data)

    def accept_message(self, message_id: int, event: Webinar.Event) -> None:
        self.ensure_session()
        payload = {'isModerated': 'true', 'messageIds[0]': message_id}
        route = Webinar.Routes.ACCEPT_MESSAGE.format(session_id=event.session_id)
        self.session.put(route, data=payload)

    def delete_message(self, message_id: int, event: Webinar.Event) -> None:
        self.ensure_session()
        payload = {'messageIds[0]': message_id}
        route = Webinar.Routes.DELETE_MESSAGE.format(session_id=event.session_id)
        self.session.put(route, data=payload)


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars', default='avatar.svg')
    webinar_session = models.OneToOneField(WebinarSession, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        if self.id is None:
            self.webinar_session = WebinarSession.objects.create()
        super(User, self).save(*args, **kwargs)
