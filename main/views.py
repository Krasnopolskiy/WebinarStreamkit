from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth import forms as auth_forms
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView

from . import forms


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class CustomLoginView(SuccessMessageMixin, LoginView):
    context = {'pagename': 'Login'}
    template_name = 'registration/login.html'
    form_class = forms.LoginForm
    success_url = '/profile'
    success_message = 'Пользователь успешно авторизован'


class SignupView(SuccessMessageMixin, CreateView):
    context = {'pagename': 'Signup'}
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
    form_class = forms.SignupForm
    success_message = "Пользователь успешно зарегистрирован"
#    messages.add_message(self.request, messages.ERROR, 'We could not process your request at this time.')

    # def get(self, request: HttpRequest) -> HttpResponse:
    #     self.context['form'] = forms.SignupForm()
    #     return render(request, 'registration/signup.html', self.context)
    #
    # def post(self, request: HttpRequest) -> HttpResponse:
    #     get_user_model()
    #     form = forms.SignupForm(request.POST)
    #     self.context['form'] = form
    #     if form.is_valid():
    #         user = form.save()
    #         login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    #         messages.add_message(
    #             request,
    #             messages.SUCCESS,
    #             'Пользователь успешно зарегистрирован',
    #             extra_tags='alert-success'
    #         )
    #         return redirect(reverse('index'))
    #     messages.add_message(
    #         request,
    #         messages.ERROR,
    #         'Ошибка регистрации',
    #         extra_tags='alert-danger'
    #     )
    #     return render(request, 'registration/signup.html', self.context)


class ProfileView(View):
    context = {'pagename': 'Profile'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        return render(request, 'pages/profile.html', self.context)
