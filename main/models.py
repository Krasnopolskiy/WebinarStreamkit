from django.contrib.auth.models import AbstractUser
from django.db import models


class WebinarSession(models.Model):
    email = models.CharField(max_length=255, default='')
    password = models.CharField(max_length=255, default='')


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars', default='avatar.svg')
    webinar_session = models.OneToOneField(WebinarSession, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        if self.id is None:
            self.webinar_session = WebinarSession.objects.create()
        super(User, self).save(*args, **kwargs)
