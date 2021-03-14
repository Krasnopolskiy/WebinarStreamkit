from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя с аватаром и ключом API

    :param avatar: ссылка на изображение
    :param apikey: Ключ API
    """
    avatar = models.CharField(max_length=255, default='')
    apikey = models.CharField(max_length=32, default='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')


class Image(models.Model):
    """
    Модель изображения для аватара

    :param image: изображение
    """
    image = models.ImageField(upload_to='images')
