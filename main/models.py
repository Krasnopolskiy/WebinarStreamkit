import json

import requests
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.CharField(max_length=255, default='')
    apikey = models.CharField(max_length=32, default='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    webinar_email = models.CharField(max_length=255, default='')
    webinar_password = models.CharField(max_length=255, default='')
    organizationId = models.IntegerField(default=0)
    id = models.IntegerField(default=0, primary_key=True)
    sessionId = models.IntegerField(default=0)


class Image(models.Model):
    image = models.ImageField(upload_to='images')


class DBModel:
    def __init__(self):
        pass

    def get_user(self, login):
        return User.objects.get(username=login)

    def get_apikey(self, login):
        return self.get_user(login).apikey

    def set_apikey(self, apikey, username):
        user = self.get_user(username)
        user.apikey = apikey
        self.save_user(user)

    def set_avatar(self, avatar, username):
        user = self.get_user(username)
        user.avatar = avatar.image.url
        self.save_user(user)

    def set_webinar_account(self, webinar_email, webinar_password, username):
        user = self.get_user(username)
        user.webinar_email = webinar_email
        user.webinar_password = webinar_password

        session = requests.Session()
        session.post('https://events.webinar.ru/api/login',
                     data={'email': user.webinar_email, 'password': user.webinar_password})
        json_resp = json.loads(session.get('https://events.webinar.ru/api/login').text)
        user.organizationId = json_resp['memberships'][0]['organization']['id']

        user.save()

    def save_user(self, user):
        user.save()
