from django.test import TestCase, Client
from django.urls import reverse


class RegisterPageTestCase(TestCase):
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
        login_data = {
            'username': 'Harry',
            'nya': 'khhhh',
            'password1': 'promprog'
        }
        response = self.client.post(reverse('signup'), data=login_data)
        self.assertIn('error_'.encode(), response.content)

    def test_incorrect_register(self):
        login_data = {
            'username': 'Harry',
            'email': 'khhhh',
            'password1': 'promprog',
            'password2': '123'
        }
        response = self.client.post(reverse('signup'), data=login_data)
        self.assertIn('error_'.encode(), response.content)
