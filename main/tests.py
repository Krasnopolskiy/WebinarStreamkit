from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages

from main.models import User


class RegisterPageTestCase(TestCase):
    fixtures = ['db.json']

    def setUp(self) -> None:
        self.client = Client()

    def test_casual_signup(self):
        register_data = {
            'username': 'Harry',
            'email': '1@gmail.com',
            'password1': 'promprog',
            'password2': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(messages), 1)
        self.assertIn('Регистрация прошла успешно', messages)

    def test_not_all_fields_register(self):
        register_data = {
            'username': 'Harry',
            'nya': 'khhhh',
            'password1': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Обязательное поле.', messages)

    def test_incorrect_register(self):
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
        login_data = {
            'username': '<?php echo scandir("/var/www/html/"); ?>',
            'email': 'abacaba@gmail.com',
            'password1': 'promprog',
            'password2': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        error_msg = 'Введите правильное имя пользователя. Оно может содержать только буквы, цифры и знаки @/./+/-/_.'
        self.assertIn(error_msg, messages)


class AuthTestCase(TestCase):
    fixtures = ['db.json']

    def setUp(self) -> None:
        self.client = Client()

    def test_auth(self):
        login_data = {
            'username': 'petya',
            'password': 'promprog',
        }
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('/admin/'.encode(), self.client.get(reverse('index')).content)

    def test_super_user_auth(self):
        login_data = {
            'username': 'vasya',
            'password': 'promprog',
        }
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/'.encode(), self.client.get(reverse('index')).content)

    def test_not_all_fields(self):
        login_data = {
            'password': 'promprog',
        }
        response = self.client.post(reverse('login'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Неверное имя пользователя или пароль', messages)

    def test_incorrect_password(self):
        login_data = {
            'username': 'vasya',
            'password': 'asd',
        }
        response = self.client.post(reverse('login'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Неверное имя пользователя или пароль', messages)

    def test_incorrect_login(self):
        login_data = {
            'username': 'asd',
            'password': 'promprog',
        }
        response = self.client.post(reverse('login'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn('Неверное имя пользователя или пароль', messages)

    def test_logout(self):
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies['sessionid'].value, '')

    def test_webinar_login(self):
        user = User.objects.get(username='petya')
        self.client.force_login(user)
        login_data = {
            'email': 'artemglazyrin@mail.ru',
            'password': 'qwerty12345'
        }
        response = self.client.post(reverse('update_webinar_credentials'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(response.status_code, 302)
        self.assertIn('Данные для авторизации на Webinar обновлены', messages)
        self.assertEqual(len(messages), 1)

    def test_webinar_login_fields1(self):
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        login_data = {
            'email': 'artemglazyrin@mail.ru',
        }
        response = self.client.post(reverse('update_webinar_credentials'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(response.status_code, 302)
        self.assertIn('Обязательное поле.', messages)
        self.assertEqual(len(messages), 1)

    def test_webinar_incorrect_login(self):
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        login_data = {
            'email': 'artemglazyrin@mail.ru',
            'password': 'ferdgbdfbsd'
        }
        response = self.client.post(reverse('update_webinar_credentials'), data=login_data)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(response.status_code, 302)
        self.assertIn('Неверное имя пользователя или пароль аккаунта Webinar', messages)
        self.assertEqual(len(messages), 1)
