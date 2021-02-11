from django_registration.forms import RegistrationForm
from django import forms


class SignUpForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        username = forms.CharField(
            widget=forms.TextInput,
            label='Имя пользователя'
        )
