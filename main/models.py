from datetime import date, timedelta
from functools import wraps
from http.cookiejar import Cookie
from json import loads
from typing import Dict, List, Optional, Union

from django.contrib.auth.models import AbstractUser
from django.db import models
from requests import Session

from main.webinar import EventRouter, MessageRouter, UserRouter, Webinar


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

    def login(self) -> Optional[Webinar.Error]:
        route = UserRouter.LOGIN.value
        payload = {'email': self.email, 'password': self.password}
        response = loads(self.session.post(route, data=payload).text)
        if 'error' in response:
            self.last_login = None
            self.save()
            return Webinar.Error(response.get('error'))
        data = loads(self.session.get(route).text)
        self.user_id = data.get('id')
        self.last_login = date.today()
        self.cookie = self.get_cookie('sessionId').value
        self.save()

    def is_login_required(self) -> bool:
        return self.last_login is None or date.today() - self.last_login > timedelta(weeks=1)

    def ensure_session(self) -> Optional[Webinar.Error]:
        if self.is_login_required():
            error = self.login()
            if error is not None:
                return error
        self.session.cookies.set('sessionId', self.cookie)

    def webinar_required(function):
        @wraps(function)
        def wrap(self, *args, **kwargs):
            response = self.ensure_session()
            if isinstance(response, Webinar.Error):
                return response
            return function(self, *args, **kwargs)
        return wrap

    @webinar_required
    def get_user(self) -> Union[Webinar.User, Webinar.Error]:
        route = UserRouter.INFO.value.format(user_id=self.user_id)
        data = loads(self.session.get(route).text)
        return Webinar.User(data, True)

    @webinar_required
    def get_schedule(self) -> Union[List[Webinar.Event], Webinar.Error]:
        schedule = list()
        user = self.get_user()
        for organisation in user.memberships:
            route = EventRouter.PLANNED.value.format(organization_id=organisation.id)
            events = loads(self.session.get(route).text)
            schedule += list(filter(
                lambda event: event is not None,
                [self.get_event(event.get('eventId', event['id'])) for event in events]
            ))
        return schedule

    @webinar_required
    def get_event(self, event_id: int) -> Union[Webinar.Event, Webinar.Error]:
        route = EventRouter.INFO.value.format(event_id=event_id)
        data = loads(self.session.get(route).text)
        if 'error' not in data:
            return Webinar.Event(self.user_id, data)

    @webinar_required
    def get_chat(self, session_id: int) -> Union[Webinar.Chat, Webinar.Error]:
        route = MessageRouter.CHAT.value.format(session_id=session_id)
        data = loads(self.session.get(route).text)
        return Webinar.Chat(data)

    @webinar_required
    def accept_message(self, session_id: int, **kwargs) -> Optional[Webinar.Error]:
        payload = {'isModerated': 'true', 'messageIds[0]': kwargs.get('message_id')}
        route = MessageRouter.ACCEPT.value.format(session_id=session_id)
        self.session.put(route, data=payload)

    @webinar_required
    def delete_message(self, session_id: int, **kwargs) -> Optional[Webinar.Error]:
        payload = {'messageIds[0]': kwargs.get('message_id')}
        route = MessageRouter.DELETE.value.format(session_id=session_id)
        self.session.put(route, data=payload)

    @webinar_required
    def update_settings(self, session_id: int, **kwargs) -> Optional[Webinar.Error]:
        route = MessageRouter.SETTINGS.value.format(session_id=session_id)
        self.session.put(route, data=kwargs)

    @webinar_required
    def start(self, session_id: int, **kwargs) -> Optional[Webinar.Error]:
        route = EventRouter.START.value.format(session_id=session_id)
        self.session.put(route)

    @webinar_required
    def stop(self, session_id: int, **kwargs) -> Optional[Webinar.Error]:
        route = EventRouter.STOP.value.format(session_id=session_id)
        self.session.put(route)


class User(AbstractUser):
    """
    Модель пользователя с аватаром и ключом API

    :param avatar: ссылка на изображение
    :param webinar_session: ForeignKey на модель сессии
    """
    avatar = models.ImageField(upload_to='avatars', default='avatar.svg')
    webinar_session = models.OneToOneField(WebinarSession, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        if self.id is None:
            self.webinar_session = WebinarSession.objects.create()
        super(User, self).save(*args, **kwargs)
