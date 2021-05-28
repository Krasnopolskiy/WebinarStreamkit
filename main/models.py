from datetime import date, timedelta
from functools import wraps
from http.cookiejar import Cookie
from json import loads
from typing import Callable, Optional

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from requests import Session, post

from main.webinar import EventRouter, MessageRouter, UserRouter, Webinar


class WebinarSession(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True)
    email = models.EmailField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)
    cookie = models.CharField(max_length=32, null=True)
    last_login = models.DateField(null=True)

    session = Session()

    def get_cookie(self, cookie_name: str) -> Cookie:
        """
        Получение Cookie пользователя
        :param cookie_name:
        :return: Cookie
        """
        for cookie in self.session.cookies:
            if cookie.name == cookie_name:
                return cookie

    def is_correct_data(self, check_email: str, check_password: str) -> bool:
        """
        Проверка на наличие аккаунта на webinar
        :param check_email: email пользователя
        :param check_password: пароль пользователя
        :return: Существует пользователь или нет
        """
        route = UserRouter.LOGIN.value
        payload = {'email': check_email, 'password': check_password, 'rememberMe': 'true'}
        response = loads(post(route, data=payload).text)
        return 'error' not in response

    def login(self) -> Optional[Webinar.Error]:
        """
        Вход в аккаунт webinar через наш сервис
        """
        self.session = Session()
        route = UserRouter.LOGIN.value
        payload = {'email': self.email, 'password': self.password, 'rememberMe': 'true'}
        response = loads(self.session.post(route, data=payload).text)
        data = loads(self.session.get(route).text)
        if 'error' in response:
            self.last_login = None
            self.save()
            return Webinar.Error(response.get('error'))
        self.user_id = data.get('id')
        self.last_login = date.today()
        self.cookie = self.get_cookie('sessionId').value
        self.save()

    def is_login_required(self) -> bool:
        """
        Проверка на необходимость повторного входа в аккаунт webinar
        :return:
        """
        return self.last_login is None or date.today() - self.last_login > timedelta(weeks=1)

    def ensure_session(self) -> Optional[Webinar.Error]:
        if self.is_login_required():
            error = self.login()
            if error is not None:
                return error
        self.session.cookies.set('sessionId', self.cookie)

    def webinar_required(function: Callable):
        @wraps(function)
        def wrap(self, *args, **kwargs):
            response = self.ensure_session()
            if isinstance(response, Webinar.Error):
                return response
            try:
                return function(self, *args, **kwargs)
            except:
                return Webinar.Error({'message': 'error'})
        return wrap

    @webinar_required
    def get_user(self):
        """
        Получение пользователя
        :return: Объект пользователя webinar
        """
        if not self.user_id:
            self.login()
        route = UserRouter.INFO.value.format(user_id=self.user_id)
        data = loads(self.session.get(route).text)
        return Webinar.User(data, True)

    @webinar_required
    def get_schedule(self):
        """
        Получение расписания вебинаров
        :return: Расписание вебинаров
        """
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
    def get_event(self, event_id: int):
        """
        Получение вебинара (события)
        :param event_id: id события
        :return: Объект события
        """
        route = EventRouter.INFO.value.format(event_id=event_id)
        data = loads(self.session.get(route).text)
        if 'error' not in data:
            return Webinar.Event(self.user_id, data)

    @webinar_required
    def get_chat(self, session_id: int):
        """
        Получение чата
        :return: Чат из вебинара
        """
        route = MessageRouter.CHAT.value.format(session_id=session_id)
        messages = loads(self.session.get(route).text)
        route = MessageRouter.SETTINGS.value.format(session_id=session_id)
        settings = loads(self.session.get(route).text)
        return Webinar.Chat(messages, settings)

    @webinar_required
    def accept_message(self, session_id: int, **kwargs):
        """
        Принятие сообщений
        """
        payload = {'isModerated': 'true', 'messageIds[0]': kwargs.get('message_id')}
        route = MessageRouter.ACCEPT.value.format(session_id=session_id)
        self.session.put(route, data=payload)

    @webinar_required
    def delete_message(self, session_id: int, **kwargs):
        """
        Удаление сообщений
        """
        payload = {'messageIds[0]': kwargs.get('message_id')}
        route = MessageRouter.DELETE.value.format(session_id=session_id)
        self.session.put(route, data=payload)

    @webinar_required
    def update_settings(self, session_id: int, **kwargs):
        """
        Обновление настроек
        :param session_id:
        :param kwargs:
        :return:
        """
        route = MessageRouter.SETTINGS.value.format(session_id=session_id)
        resp = self.session.put(route, data=kwargs)
        print(resp.text)

    @webinar_required
    def start(self, session_id: int, **kwargs):
        """
        Начать вебинар
        :param session_id: id сессии
        """
        route = EventRouter.START.value.format(session_id=session_id)
        self.session.put(route)

    @webinar_required
    def stop(self, session_id: int, **kwargs):
        """
        Закончить вебинар
        :param session_id: id сессии
        """
        route = MessageRouter.STOP.value.format(session_id=session_id)
        self.session.put(route)


class User(AbstractUser):
    """
    Модель пользователя

    :param webinar_session: ForeignKey на модель сессии
    :param fontsize: Размер шрифта виджетов
    """
    id = models.AutoField(primary_key=True)
    webinar_session = models.OneToOneField(WebinarSession, on_delete=models.CASCADE)
    fontsize = models.IntegerField(
        default=16,
        validators=[
            MinValueValidator(8),
            MaxValueValidator(48)
        ]
    )

    def save(self, *args, **kwargs) -> None:
        """
        Сохранение пользователя
        """
        if self.id is None:
            self.webinar_session = WebinarSession.objects.create()
        super(User, self).save(*args, **kwargs)

    def update_fontsize(self, *args, **kwargs) -> None:
        """
        Обновление размера шрифта у пользователя
        """
        fontsize = kwargs.get('fontsize', '16')
        if fontsize.isdigit():
            fontsize = int(fontsize)
            fontsize = min(fontsize, 48)
            fontsize = max(fontsize, 8)
            self.fontsize = fontsize
            self.save()
