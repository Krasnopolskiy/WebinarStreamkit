from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.CharField(max_length=255, default='')
    apikey = models.CharField(max_length=32, default='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    webinar_email = models.CharField(max_length=255, default='')
    webinar_password = models.CharField(max_length=255, default='')
    organizationId = models.IntegerField(default=0)


class Image(models.Model):
    image = models.ImageField(upload_to='images')
