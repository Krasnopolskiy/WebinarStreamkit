from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from main.forms import UserInformationForm, WebinarCredentialsForm


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class ProfileView(LoginRequiredMixin, View):
    context = {'pagename': 'Profile'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['forms'] = {
            'information': UserInformationForm(),
            'password': PasswordChangeForm(user=request.user),
            'webinar': WebinarCredentialsForm()
        }
        self.context['webinar_user'] = request.user.webinar_session.get_user()
        return render(request, 'pages/profile.html', self.context)


class WebinarCredentialsView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponsePermanentRedirect:
        form = WebinarCredentialsForm(request.POST, instance=request.user.webinar_session)
        if form.is_valid():
            form.save()
        return redirect(reverse('profile'))


class UserInformationView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponsePermanentRedirect:
        form = UserInformationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect(reverse('profile'))


class ScheduleView(LoginRequiredMixin, View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['events'] = request.user.webinar_session.get_schedule()
        return render(request, 'pages/schedule.html', self.context)


class EventView(LoginRequiredMixin, View):
    context = {'pagename': 'Event'}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        self.context['event'] = request.user.webinar_session.get_event({'id': event_id})
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
        self.context['event'] = request.user.webinar_session.get_event({'id': event_id})
        return render(request, 'pages/control.html', self.context)
