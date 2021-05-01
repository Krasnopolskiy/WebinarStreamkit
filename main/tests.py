from django.test import TestCase, Client
from django.urls import reverse

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
        self.assertEqual(response.status_code, 302)

    def test_not_all_fields_register(self):
        register_data = {
            'username': 'Harry',
            'nya': 'khhhh',
            'password1': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        errors = response.context_data['view'].form_class.error_messages.values()
        self.assertIn('Введенные пароли не совпадают.', errors)

    def test_incorrect_register(self):  # Проверить на ошибки
        register_data = {
            'username': 'Harry',
            'email': 'khhhh',
            'password1': 'promprog',
            'password2': '123'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        errors = response.context_data['view'].form_class.error_messages.values()
        self.assertIn('Введенные пароли не совпадают.', errors)

    def test_exist_register(self):  # Проверить на ошибки
        register_data = {
            'username': 'vasya',
            'email': '1@gmail.com',
            'password1': 'promprog',
            'password2': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=register_data)
        self.assertIn('error_'.encode(), response.content)


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

    def test_not_all_fields(self):  # Проверить на ошибки
        login_data = {
            'password': 'promprog',
        }
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 200)

    def test_incorrect_fields(self):  # Проверить на ошибки
        login_data = {
            'username': 'vasya',
            'password': 'asd',
        }
        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        user = User.objects.get(username='vasya')
        self.client.force_login(user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies['sessionid'].value, '')

