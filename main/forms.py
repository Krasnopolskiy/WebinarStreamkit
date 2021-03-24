from django import forms
from django_registration.forms import RegistrationForm

from main.models import User, WebinarSession


class ExtendedSignupForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class UserInformationForm(forms.ModelForm):
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Загрузить аватар'
    )

    class Meta:
        model = User
        fields = ['avatar']


class WebinarCredentialsForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput,
        label='Адрес электронной почты Webinar'
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль Webinar'
    )

    class Meta:
        model = WebinarSession
        fields = ['email', 'password']
