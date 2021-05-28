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

from main.forms import (ExtendedRegistrationForm, WebhooksForm,
                        WebinarCredentialsForm)
from main.models import DiscordHistory
from main.webinar import BaseRouter, Webinar


class ExtendedLoginView(LoginView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = super(LoginView, self).post(request, *args, **kwargs)
        if request.user.is_authenticated:
            messages.success(request, "Авторизация прошла успешно")
        else:
            messages.error(request, "Неверное имя пользователя или пароль")
        return response


class ExtendedRegistrationView(RegistrationView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ExtendedRegistrationForm(request.POST)
        for scope in form.errors.values():
            for error in list(scope):
                messages.error(request, error)
        response = super().post(request, *args, **kwargs)
        if request.user.is_authenticated:
            messages.success(request, "Регистрация прошла успешно")
        return response


class IndexView(View):
    """
    View-класс главной страницы
    """

    context = {"pagename": "Index"}

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        View-функция главной страницы (GET)

        :param request: Детали запроса
        :type request: :class: `django.http.HttpRequest`
        :return: Объект ответа сервера
        :rtype: :class: `django.http.HttpResponse`
        """
        return render(request, "pages/index.html", self.context)


class ProfileView(LoginRequiredMixin, View):
    """
    View-класс профиля
    """

    context = {"pagename": "Profile"}

    def get(self, request: HttpRequest) -> HttpResponse:
        response = request.user.webinar_session.get_user()
        self.context["forms"] = {
            "password": PasswordChangeForm(user=request.user),
            "webinar": WebinarCredentialsForm(
                initial={"email": request.user.webinar_session.email}
            ),
        }
        self.context["error"] = (
            response.message if isinstance(response, Webinar.Error) else None
        )
        self.context["webinar_user"] = request.user.webinar_session.get_user()
        return render(request, "pages/profile.html", self.context)


class WebinarCredentialsUpdateView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponsePermanentRedirect:
        form = WebinarCredentialsForm(
            request.POST, instance=request.user.webinar_session
        )
        self.set_messages(request, form)
        for scope in form.errors.values():
            for error in list(scope):
                messages.error(request, error)
        return redirect(reverse("profile"))

    def set_messages(self, request, form):
        """
        Метод для добавления сообщений при авторизации на webinar через наш сервис
        :param request:
        :param form:
        :return:
        """
        if form.is_valid():
            if request.user.webinar_session.is_correct_data(
                request.POST["email"],
                request.POST["password"]
            ):
                form.save()
                request.user.webinar_session.login()
                messages.success(request, "Данные для авторизации на Webinar обновлены")
            else:
                messages.error(
                    request, "Неверное имя пользователя или пароль аккаунта Webinar"
                )


class WebinarCredentialsDeleteView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponsePermanentRedirect:
        request.user.webinar_session.logout()
        messages.warning(request, "Данные для авторизации на Webinar удалены")
        return redirect(reverse("profile"))


class ScheduleView(LoginRequiredMixin, View):
    """
    View-класс списка вебинаров
    """

    context = {"pagename": "Schedule"}

    def get(self, request: HttpRequest) -> HttpResponse:
        response = request.user.webinar_session.get_schedule()
        if isinstance(response, Webinar.Error):
            messages.error(request, response.message)
            return redirect(reverse("index"))
        self.context["events"] = response
        self.context["webinar_url"] = BaseRouter.EVENTS.value.format(route="")
        return render(request, "pages/schedule.html", self.context)


class EventView(LoginRequiredMixin, View):
    """
    View-класс вебинара
    """

    context = {"pagename": "Event"}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        response = request.user.webinar_session.get_event(event_id)
        if isinstance(response, Webinar.Error):
            messages.error(request, response.message)
            return redirect(reverse("index"))
        self.context["event"] = response
        self.context["form"] = WebhooksForm()
        return render(request, "pages/event.html", self.context)

    def post(self, request: HttpRequest, event_id: int) -> HttpResponse:
        form = WebhooksForm(request.POST)
        if form.is_valid():
            webhooks = [webhook.strip() for webhook in form.cleaned_data.get('webhooks').splitlines()]
            history = DiscordHistory.objects.filter(event_id=event_id)
            if history.exists():
                history = history.first()
                history.webhooks = webhooks
            else:
                history = DiscordHistory(event_id=event_id, webhooks=webhooks)
            history.save()
            messages.success(request, "Информация обновлена")
        return redirect(reverse('event', args=[event_id]))


class ChatView(LoginRequiredMixin, View):
    context = {"pagename": "Chat"}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        return render(request, "pages/chat.html", self.context)


class AwaitingMessagesView(LoginRequiredMixin, View):
    context = {"pagename": "Awaiting"}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        return render(request, "pages/awaiting.html", self.context)


class ControlView(LoginRequiredMixin, View):
    context = {"pagename": "Control"}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        self.context["event"] = request.user.webinar_session.get_event(event_id)
        self.context["fontsize"] = request.user.fontsize
        return render(request, "pages/control.html", self.context)
