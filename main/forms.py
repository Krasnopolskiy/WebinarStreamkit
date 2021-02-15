from django_registration.forms import RegistrationForm
from django import forms
from django.contrib.auth import get_user_model

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
