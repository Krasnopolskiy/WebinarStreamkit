from django_registration.forms import RegistrationForm
from django import forms

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
        username = forms.CharField(
            widget=forms.TextInput,
            label='Имя пользователя'
        )
