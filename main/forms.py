from django import forms

class LogInForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput,
        label='Имя пользователя'
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )
