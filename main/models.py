from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.CharField(max_length=255, default='')
    apikey = models.CharField(max_length=32, default='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    service_email = models.CharField(max_length=255, default='krimiussp@gmail.com')
    service_password = models.CharField(max_length=255, default='promprog')


class Image(models.Model):
    image = models.ImageField(upload_to='images')
