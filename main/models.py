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
