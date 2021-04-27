from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django_registration.backends.one_step.views import RegistrationView

from main.forms import (ExtendedRegistrationForm, UserInformationForm,
                        WebinarCredentialsForm)
from main.webinar import BaseRouter, Webinar


class ExtendedLoginView(LoginView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = super(LoginView, self).post(request, *args, **kwargs)
        if request.user.is_authenticated:
            messages.success(request, 'Авторизация прошла успешно')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
        return response


class ExtendedRegistrationView(RegistrationView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # TODO Исправить отображение ошибки "Пользователь с таким именем уже существует"
        form = ExtendedRegistrationForm(request.POST)
        response = super(RegistrationView, self).post(request, *args, **kwargs)
        if request.user.is_authenticated:
            messages.success(request, 'Регистрация прошла успешно')
        for scope in form.errors.values():
            for error in list(scope):
                messages.error(request, error)
        return response


class IndexView(View):
    """
    View-класс главной страницы
    """
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        View-функция главной страницы (GET)

        :param request: Детали запроса
        :type request: :class: `django.http.HttpRequest`
        :return: Объект ответа сервера
        :rtype: :class: `django.http.HttpResponse`
        """
        return render(request, 'pages/index.html', self.context)


class ProfileView(LoginRequiredMixin, View):
    """
    View-класс профиля
    """
    context = {'pagename': 'Profile'}

    def get(self, request: HttpRequest) -> HttpResponse:
        response = request.user.webinar_session.get_user()
        self.context['forms'] = {
            'information': UserInformationForm(),
            'password': PasswordChangeForm(user=request.user),
            'webinar': WebinarCredentialsForm(initial={
                'email': request.user.webinar_session.email
            })
        }
        self.context['error'] = response.message if isinstance(response, Webinar.Error) else None
        self.context['webinar_user'] = request.user.webinar_session.get_user()
        return render(request, 'pages/profile.html', self.context)


class WebinarCredentialsView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponsePermanentRedirect:
        form = WebinarCredentialsForm(request.POST, instance=request.user.webinar_session)
        if form.is_valid():
            form.save()
            request.user.webinar_session.login()
            messages.success(request, 'Данные для авторизации на Webinar обновлены')
        for scope in form.errors.values():
            for error in list(scope):
                messages.error(request, error)
        return redirect(reverse('profile'))


class UserInformationView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponsePermanentRedirect:
        form = UserInformationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аватар обновлен')
        for scope in form.errors.values():
            for error in list(scope):
                messages.error(request, error)
        return redirect(reverse('profile'))


class ScheduleView(LoginRequiredMixin, View):
    """
    View-класс списка вебинаров
    """
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        response = request.user.webinar_session.get_schedule()
        if isinstance(response, Webinar.Error):
            messages.error(request, response.message)
            return redirect(reverse('index'))
        self.context['events'] = response
        self.context['webinar_url'] = BaseRouter.EVENTS.value.format(route='')
        return render(request, 'pages/schedule.html', self.context)


class EventView(LoginRequiredMixin, View):
    """
    View-класс вебинара
    """
    context = {'pagename': 'Event'}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        self.context['event'] = request.user.webinar_session.get_event(event_id)
        return render(request, 'pages/event.html', self.context)


class ChatView(LoginRequiredMixin, View):
    context = {'pagename': 'Chat'}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        return render(request, 'pages/chat.html', self.context)


class AwaitingMessagesView(LoginRequiredMixin, View):
    context = {'pagename': 'Awaiting'}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        return render(request, 'pages/awaiting.html', self.context)


class ControlView(LoginRequiredMixin, View):
    context = {'pagename': 'Control'}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        self.context['event'] = request.user.webinar_session.get_event(event_id)
        return render(request, 'pages/control.html', self.context)
