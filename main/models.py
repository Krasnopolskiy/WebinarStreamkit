from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.CharField(max_length=255, default='')
    apikey = models.CharField(max_length=32, default='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')


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

    def save_user(self, user):
        user.save()
