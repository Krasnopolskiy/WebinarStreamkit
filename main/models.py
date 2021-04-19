from datetime import date, timedelta
from http.cookiejar import Cookie
from json import loads
from typing import Dict, List, Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from requests import Session

from main.webinar import Webinar


class WebinarSession(models.Model):
    user_id = models.IntegerField(null=True)
    email = models.EmailField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)

    cookie = models.CharField(max_length=32, null=True)
    last_login = models.DateField(null=True)

    session = Session()

    def get_cookie(self, cookie_name: str) -> Optional[Cookie]:
        for cookie in self.session.cookies:
            if cookie.name == cookie_name:
                return cookie

    def login(self) -> Optional[Dict]:
        route = Webinar.Routes.LOGIN
        payload = {'email': self.email, 'password': self.password}
        response = loads(self.session.post(route, data=payload).text)
        if 'error' in response:
            return response
        data = loads(self.session.get(route, data=payload).text)
        self.user_id = data.get('id')
        self.last_login = date.today()
        self.cookie = self.get_cookie('sessionId').value
        self.save()

    def is_login_required(self) -> bool:
        return self.last_login is None or date.today() - self.last_login > timedelta(weeks=1)

    def ensure_session(self) -> Optional[Dict]:
        if self.is_login_required():
            errors = self.login()
            return errors if errors else None
        self.session.cookies.set('sessionId', self.cookie)

    def get_user(self) -> Webinar.User:
        errors = self.ensure_session()
        route = Webinar.Routes.USER.format(user_id=self.user_id)
        data = loads(self.session.get(route).text)
        return Webinar.User(data, True)

    def get_schedule(self) -> List[Webinar.Event]:
        errors = self.ensure_session()
        schedule = list()
        user = self.get_user()
        for organisation in user.memberships:
            route = Webinar.Routes.PLANNED.format(organization_id=organisation.id)
            events = loads(self.session.get(route).text)
            schedule += list(filter(
                lambda event: event is not None,
                [self.get_event(event.get('id')) for event in events]
            ))
        return schedule

    def get_event(self, event_id: int) -> Webinar.Event:
        errors = self.ensure_session()
        route = Webinar.Routes.EVENT.format(event_id=event_id)
        data = loads(self.session.get(route).text)
        if 'error' not in data:
            return Webinar.Event(self.user_id, data)

    def get_chat(self, session_id: int) -> Webinar.Chat:
        errors = self.ensure_session()
        route = Webinar.Routes.CHAT.format(session_id=session_id)
        data = loads(self.session.get(route).text)
        return Webinar.Chat(data)

    def accept_message(self, session_id: int, **kwargs) -> None:
        errors = self.ensure_session()
        payload = {'isModerated': 'true', 'messageIds[0]': kwargs.get('message_id')}
        route = Webinar.Routes.ACCEPT_MESSAGE.format(session_id=session_id)
        self.session.put(route, data=payload)

    def delete_message(self, session_id: int, **kwargs) -> None:
        errors = self.ensure_session()
        payload = {'messageIds[0]': kwargs.get('message_id')}
        route = Webinar.Routes.DELETE_MESSAGE.format(session_id=session_id)
        self.session.put(route, data=payload)

    def update_settings(self, session_id: int, **kwargs) -> None:
        errors = self.ensure_session()
        route = Webinar.Routes.SETTINGS.format(session_id=session_id)
        self.session.put(route, data=kwargs).text

    def start(self, session_id: int) -> None:
        errors = self.ensure_session()
        route = Webinar.Routes.START.format(session_id=session_id)
        self.session.put(route)

    def stop(self, session_id: int) -> None:
        errors = self.ensure_session()
        route = Webinar.Routes.STOP.format(session_id=session_id)
        self.session.put(route)


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars', default='avatar.svg')
    webinar_session = models.OneToOneField(WebinarSession, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        if self.id is None:
            self.webinar_session = WebinarSession.objects.create()
        super(User, self).save(*args, **kwargs)
