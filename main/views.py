from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth import forms as auth_forms
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from django.urls import reverse
from django.contrib import messages

from . import forms


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class LoginView(View):
    context = {'pagename': 'Login'}

    def get(self, request):
        self.context['form'] = forms.LoginForm()
        return render(request, 'registration/login.html', self.context)

    def post(self, request):
        get_user_model()
        form = forms.LoginForm(request.POST)
        self.context['form'] = form
        if form.is_valid():
            self.context['form_error'] = False
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Пользователь успешно авторизован',
                    extra_tags='alert-success'
                )
                return redirect(reverse('index'))
            messages.add_message(
                request,
                messages.ERROR,
                'Неправильный логин или пароль',
                extra_tags='alert-danger'
            )
            return render(request, 'registration/login.html', self.context)
        messages.add_message(
            request,
            messages.ERROR,
            'Некорректные данные в форме авторизации',
            extra_tags='alert-danger'
        )
        return render(request, 'registration/login.html', self.context)


class SignupView(View):
    context = {'pagename': 'Signup'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['form'] = forms.SignupForm()
        return render(request, 'registration/signup.html', self.context)

    def post(self, request: HttpRequest) -> HttpResponse:
        get_user_model()
        form = forms.SignupForm(request.POST)
        self.context['form'] = form
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Пользователь успешно зарегистрирован',
                extra_tags='alert-success'
            )
            return redirect(reverse('index'))
        messages.add_message(
            request,
            messages.ERROR,
            'Ошибка регистрации',
            extra_tags='alert-danger'
        )
        return render(request, 'registration/signup.html', self.context)


class ProfileView(View):
    context = {'pagename': 'Profile'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        return render(request, 'pages/profile.html', self.context)


class ScheduleView(View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/schedule.html', self.context)
