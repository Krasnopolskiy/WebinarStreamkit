from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from bs4 import BeautifulSoup
from PIL import Image
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
        self.assertRedirects(response, reverse('index'))
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
        self.assertRedirects(response, reverse('index'))
        self.assertNotIn('/admin/'.encode(), self.client.get(reverse('index')).content)

    def test_super_user_auth(self):
        login_data = {
            'username': 'special_admin',
            'password': 'r3ally_s3cr3t_p4ssw0rd',
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
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(response.cookies['sessionid'].value, '')

    def test_webinar_login(self):
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
    fixtures = ['db.json']

    def setUp(self) -> None:
        self.client = Client()
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        login_data = {
            'email': 'wstreamkit@mail.ru',
            'password': 'uTAouAOpy-51'
        }
        self.client.post(reverse('update_webinar_credentials'), data=login_data)

    def test_schedule_view(self):
        response = self.client.get(reverse('schedule'))
        self.assertEqual(response.status_code, 200)
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(len(messages), 1)
        self.assertIn('Данные для авторизации на Webinar обновлены', messages)
        self.assertIn(b'<div class="shadow-sm p-3 border rounded">', response.content)

    def test_event_view(self):
        response = self.client.get(reverse('schedule'))
        soup = BeautifulSoup(response.content, 'html.parser')
        a = [a.attrs['href'] for a in soup.findAll('a', class_='btn-outline-primary')]
        if a:
            response = self.client.get(a[0])
            self.assertEqual(response.status_code, 200)
            soup = BeautifulSoup(response.content, 'html.parser')
            buttons = soup.find('div', class_='px-3').findChildren()
            text_in_buttons = [b.text.strip() for b in buttons]
            self.assertEqual(len(text_in_buttons), 2)
            self.assertListEqual(text_in_buttons, ['Панель управления', 'Перейти к вебинару'])
        else:
            self.assertIn('Нет ни одного запланированного вебинара'.encode(), response.content)


class WidgetTestCase(TestCase):
    fixtures = ['db.json']

    def setUp(self) -> None:
        self.client = Client()
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        login_data = {
            'email': 'wstreamkit@mail.ru',
            'password': 'uTAouAOpy-51',
        }
        self.client.post(reverse('update_webinar_credentials'), data=login_data)
        response = self.client.get(reverse('schedule'))
        soup = BeautifulSoup(response.content, 'html.parser')
        a = [a.attrs['href'] for a in soup.findAll('a', class_='btn-outline-primary')]
        if not a:
            raise Exception('На аккаунте ' + login_data['email'] + ' нет ни одного вебинара.\n'
                                                                   'Создайте вебинар и снова запустите тесты')
        self.target_url = self.client.get(a[0]) + '/control'

    def test_view(self):
        # TODO: Дописать проверку виджетов, (у тестировщика не отображаются вебинары)
        response = self.client.get(self.target_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        print(soup.prettify())


class UnauthUserTestCase(TestCase):
    fixtures = ['db.json']

    def setUp(self) -> None:
        self.client = Client()
