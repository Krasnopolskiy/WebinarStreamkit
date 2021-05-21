"""
Just tests, no more
"""
# import pytest
from json import loads

from channels.testing import HttpCommunicator
from django.test import TestCase, Client
from django.test.client import AsyncClient
from django.urls import reverse
from django.contrib.messages import get_messages
from bs4 import BeautifulSoup
from PIL import Image
from requests import Session

from main.consumers import ControlConsumer
from main.webinar import BaseRouter, UserRouter
from main.models import User
# import asyncio
# import websockets


class RegisterPageTestCase(TestCase):
    """
    Тесты на регистрацию
    """
    fixtures = ['db.json']

    def setUp(self) -> None:
        """
        Предустановка начальных значений
        """
        self.client = Client()

    def test_casual_signup(self):
        """
        Тест на регистрацию
        """
        register_data = {
            'username': 'Harry',
            'email': '1@gmail.com',
            'password1': 'promprog',
            'password2': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(len(messages), 1)
        self.assertIn('Регистрация прошла успешно', messages)

    def test_not_all_fields_register(self):
        """
        Тест на регистрацию. Не все поля заданы
        """
        register_data = {
            'username': 'Harry',
            'nya': 'khhhh',
            'password1': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Обязательное поле.', messages)

    def test_incorrect_register(self):
        """
        Тест на регистрацию. Не все поля правильно заданы
        """
        register_data = {
            'username': 'Harry',
            'email': 'khhhh',
            'password1': 'promprog',
            'password2': '123'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Введенные пароли не совпадают.', messages)
        self.assertIn('Введите правильный адрес электронной почты.', messages)

    def test_exist_register(self):
        """
        Тест на регистрацию. Пользователь существует
        """
        register_data = {
            'username': 'vasya',
            'email': '1@gmail.com',
            'password1': 'promprog',
            'password2': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Пользователь с таким именем уже существует.', messages)

    def test_incorrect_data(self):
        """
        Тест на регистрацию. Неверно заданы поля
        """
        login_data = {
            'username': '<?php echo scandir("/var/www/html/"); ?>',
            'email': 'abacaba@gmail.com',
            'password1': 'promprog',
            'password2': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        error_msg = 'Введите правильное имя пользователя. ' \
                    'Оно может содержать только буквы, цифры и знаки @/./+/-/_.'
        self.assertIn(error_msg, messages)


class AuthTestCase(TestCase):
    """
    Тесты на авторизацию (В том числе и на webinar)
    """
    fixtures = ['db.json']

    def setUp(self) -> None:
        """
        Предустановка начальных значений
        """
        self.client = Client()

    def test_auth(self):
        """
        Тест на авторизацию. Обычный вход в аккаунт
        """
        login_data = {
            'username': 'petya',
            'password': 'promprog',
        }
        response = self.client.post(reverse('login'), data=login_data)
        self.assertRedirects(response, reverse('index'))
        self.assertNotIn('/admin/'.encode(), self.client.get(reverse('index')).content)

    def test_super_user_auth(self):
        """
        Тест на авторизацию. Вход в аккаунт суперпользователя
        """
        login_data = {
            'username': 'special_admin',
            'password': 'r3ally_s3cr3t_p4ssw0rd',
        }
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/'.encode(), self.client.get(reverse('index')).content)

    def test_not_all_fields(self):
        """
        Тест на авторизацию. Не все поля заданы
        """
        login_data = {
            'password': 'promprog',
        }
        response = self.client.post(reverse('login'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Неверное имя пользователя или пароль', messages)

    def test_incorrect_password(self):
        """
        Тест на авторизацию. Неверный пароль
        """
        login_data = {
            'username': 'vasya',
            'password': 'asd',
        }
        response = self.client.post(reverse('login'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Неверное имя пользователя или пароль', messages)

    def test_incorrect_login(self):
        """
        Тест на авторизацию. Неверный логин
        """
        login_data = {
            'username': 'asd',
            'password': 'promprog',
        }
        response = self.client.post(reverse('login'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Неверное имя пользователя или пароль', messages)

    def test_logout(self):
        """
        Тест на выход из аккаунта
        """
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(response.cookies['sessionid'].value, '')

    def test_webinar_login(self):
        """
        Тест на вход в аккаунт вебинара
        """
        user = User.objects.get(username='petya')
        self.client.force_login(user)
        login_data = {
            'email': 'wstreamkit@mail.ru',
            'password': 'uTAouAOpy-51'
        }
        response = self.client.post(reverse('update_webinar_credentials'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertRedirects(response, reverse('profile'))
        self.assertIn('Данные для авторизации на Webinar обновлены', messages)
        self.assertEqual(len(messages), 1)

    def test_webinar_login_fields1(self):
        """
        Тест на вход в аккаунт вебинара. Не указан пароль
        """
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        login_data = {
            'email': 'wstreamkit@mail.ru',
        }
        response = self.client.post(reverse('update_webinar_credentials'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertRedirects(response, reverse('profile'))
        self.assertIn('Обязательное поле.', messages)
        self.assertEqual(len(messages), 1)

    def test_webinar_incorrect_login(self):
        """
        Тест на вход в аккаунт вебинара. Неверно указан пароль
        """
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        login_data = {
            'email': 'wstreamkit@mail.ru',
            'password': 'ferdgbdfbsd'
        }
        response = self.client.post(reverse('update_webinar_credentials'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertRedirects(response, reverse('profile'))
        self.assertIn('Неверное имя пользователя или пароль аккаунта Webinar', messages)
        self.assertEqual(len(messages), 1)


class WebinarTestCase(TestCase):
    """
    Тесты на получение вебинаров
    """
    fixtures = ['db.json']

    def setUp(self) -> None:
        """
        Предустановка начальных значений
        """
        self.client = Client()
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        login_data = {
            'email': 'wstreamkit@mail.ru',
            'password': 'uTAouAOpy-51'
        }
        self.client.post(reverse('update_webinar_credentials'), data=login_data)

    def test_schedule_view(self):
        """
        Тест на отображение расписания
        """
        response = self.client.get(reverse('schedule'))
        self.assertEqual(response.status_code, 200)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(len(messages), 1)
        self.assertIn('Данные для авторизации на Webinar обновлены', messages)
        self.assertIn(b'<div class="shadow-sm p-3 border rounded">', response.content)

    def test_event_view(self):
        """
        Тест на отображение события
        """
        response = self.client.get(reverse('schedule'))
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.attrs['href'] for link in soup.findAll('a', class_='btn-outline-primary')]
        if links:
            response = self.client.get(links[0])
            self.assertEqual(response.status_code, 200)
            soup = BeautifulSoup(response.content, 'html.parser')
            buttons = soup.find('div', class_='px-3').findChildren()
            text_in_buttons = [b.text.strip() for b in buttons]
            self.assertEqual(len(text_in_buttons), 2)
            self.assertListEqual(text_in_buttons, ['Панель управления', 'Перейти к вебинару'])
        else:
            self.assertIn('Нет ни одного запланированного вебинара'.encode(), response.content)


class WidgetTestCase(TestCase):
    """
    Тесты на виджеты
    """
    fixtures = ['db.json']

    def setUp(self) -> None:
        """
        Предустановка начальных значений
        """
        self.client = Client()
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        self.login_data = {
            'email': 'wstreamkit@mail.ru',
            'password': 'uTAouAOpy-51',
        }
        self.client.post(reverse('update_webinar_credentials'), data=self.login_data)
        response = self.client.get(reverse('schedule'))
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.attrs['href'] for link in soup.findAll('a', class_='btn-outline-primary')]
        if not links:
            raise Exception('На аккаунте ' +
                            self.login_data['email'] +
                            ' нет ни одного вебинара.\n Создайте вебинар и снова запустите тесты')
        self.session = Session()
        self.session.post(UserRouter.LOGIN.value.format(), data=self.login_data)

        self.target_url = links[0]

    def test_view(self):
        """
        Тест на отображение панели управления
        """
        response = self.client.get(self.target_url + '/control')
        soup = BeautifulSoup(response.content, 'html.parser')
        arr = [soup.find(id='stop-btn'), soup.find(id='start-btn'),
               soup.find(id='moderate-switch'), soup.find(id='chat-btn'),
               soup.find(id='awaiting-btn'), soup.find(id='fontsize-range')]
        for element in arr:
            self.assertNotEqual(element, None)

    def test_view_chat(self):
        """
        Тест на отображение виджета сообщений
        """
        response = self.client.get(self.target_url + '/chat')
        self.assertIn('Сообщения'.encode(), response.content)

    def test_view_moderate(self):
        """
        Тест на отображение виджета модерируемых сообщений
        """
        response = self.client.get(self.target_url + '/awaiting')
        self.assertIn('Ожидают модерацию'.encode(), response.content)


class UnauthUserTestCase(TestCase):
    """
    Тесты на недоступность страниц для пользователей,
    которые не авторизовались
    """
    fixtures = ['db.json']

    def setUp(self) -> None:
        """
        Предустановка начальных значений
        """
        self.client = Client()

    def test_profile(self):
        """
        Тест на недоступность профиля
        """
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('profile'))

    def test_webinar_credentials(self):
        """
        Тест на недоступность изменения профиля
        """
        payload = {'email': 'asd@asdas',
                   'password': 'ahsudhhcnwen'}
        response = self.client.post(reverse('update_webinar_credentials'), data=payload)
        self.assertRedirects(response, reverse('login') + '?next='
                             + reverse('update_webinar_credentials'))
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(len(messages), 0)

    def test_update_user_information(self):
        """
        Тест на недоступность изменения аватара профиля
        """
        payload = {'avatar': Image.open('static/images/Hey_You.png')}
        response = self.client.post(reverse('update_user_information'), data=payload)
        self.assertRedirects(response, reverse('login') + '?next='
                             + reverse('update_user_information'))

    def test_schedule(self):
        """
        Тест на недоступность списка вебинаров
        """
        response = self.client.get(reverse('schedule'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('schedule'))


class UnauthWebinarUser(TestCase):
    """
    Тесты на недоступность страниц для пользователей,
    которые не авторизовались в webinar через наш сервис
    """
    fixtures = ['db.json']

    def setUp(self) -> None:
        """
        Предустановка начальных значений
        """
        self.client = Client()

        user = User.objects.get(username='petya')
        self.client.force_login(user)

    def test_schedule(self):
        """
        Тест на недоступность списка вебинаров без аккаунта ebinar
        """
        response = self.client.get(reverse('schedule'))
        self.assertRedirects(response, reverse('index'))
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(len(messages), 1)
        self.assertIn('Webinar: ERROR_WRONG_CREDENTIALS', messages)


class SocketsTestCase(TestCase):
    serve_static = True  # emulate StaticLiveServerTestCase
    fixtures = ['db.json']

    def setUp(self) -> None:
        self.async_client = AsyncClient()
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        self.login_data = {
            'email': 'wstreamkit@mail.ru',
            'password': 'uTAouAOpy-51',
        }
        self.client.post(reverse('update_webinar_credentials'), data=self.login_data)

        response = self.client.get(reverse('schedule'))
        soup = BeautifulSoup(response.content, 'html.parser')
        a = [a.attrs['href'] for a in soup.findAll('a', class_='btn-outline-primary')]
        if not a:
            raise Exception('На аккаунте ' + self.login_data['email'] +
                            ' нет ни одного вебинара.\n Создайте вебинар и снова запустите тесты')

        self.session = Session()
        self.session.post(UserRouter.LOGIN.value.format(), data=self.login_data)
        self.target_url = a[0]

    async def test_start_webinar(self):
        """
        Тест на функциональность кнопки начала вебинара
        """
        response = await self.async_client.get(self.target_url+'/control')
        print(response.content)
        route = BaseRouter.API.value.format(route='eventsessions?status=start')
        response = loads(self.session.get(route).text)
        if response:
            raise Exception('На аккаунте ' +
                            self.login_data['email'] +
                            'Уже есть идущие вебинары.\n '
                            'Закончите все вебинары и перезапустите тесты')
