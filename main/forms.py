from django_registration.forms import RegistrationForm
from django import forms
from django.contrib.auth import get_user_model
from main.models import Image
User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput,
        label='Имя пользователя'
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )


class SignupForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class ApikeyForm(forms.Form):
    apikey = forms.CharField(
        widget=forms.TextInput,
        label='Установить ключ API'
    )

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
