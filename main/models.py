from django.contrib.auth.models import User
from django.db import models

class AdditionalUserInfo(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=255)
