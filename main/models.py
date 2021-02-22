from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar = models.CharField(max_length=255, default='')

class AdditionalUserInfo(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=255)

class Image(models.Model):
    image = models.ImageField(upload_to='images')



