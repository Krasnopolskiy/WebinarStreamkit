from django.contrib.auth.forms import AuthenticationForm
from django_registration.forms import RegistrationForm
from django import forms
from django.contrib.auth import get_user_model
from main.models import Image
User = get_user_model()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        widget=forms.TextInput,
        label='Имя пользователя'
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )


class SignupForm(RegistrationForm):
    webinar_email = forms.CharField(
        widget=forms.TextInput,
        label='Email от аккаунта webinar'
    )
    webinar_password = forms.CharField(
        widget=forms.TextInput,
        label='Пароль от аккаунта webinar'
    )

    class Meta(RegistrationForm.Meta):
        model = User
        fields = {'username', 'email', 'webinar_email', 'webinar_password'}


class ApikeyForm(forms.Form):
    apikey = forms.CharField(
        widget=forms.TextInput,
        label='Установить ключ API'
    )


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
