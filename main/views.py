from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.http.response import HttpResponse
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
        request.user.webinar_session.login()
        self.context['name'] = request.user.webinar_session.webinar_user.name
        self.context['secondName'] = request.user.webinar_session.webinar_user.secondName
        return render(request, 'pages/profile.html', self.context)


class WebinarCredentialsView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponse:
        form = WebinarCredentialsForm(request.POST, instance=request.user.webinar_session)
        if form.is_valid():
            form.save()
        return redirect(reverse('profile'))


class UserInformationView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest) -> HttpResponse:
        form = UserInformationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect(reverse('profile'))


class ScheduleView(LoginRequiredMixin, View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        request.user.webinar_session.login()
        self.context['events'] = request.user.webinar_session.get_schedule()
        return render(request, 'pages/schedule.html', self.context)


class EventView(LoginRequiredMixin, View):
    context = {'pagename': 'Event'}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        request.user.webinar_session.login()
        self.context['event'] = request.user.webinar_session.get_event({'id': event_id})
        return render(request, 'pages/event.html', self.context)


class WidgetView(LoginRequiredMixin, View):
    context = {'pagename': 'Widget'}

    def get(self, request: HttpRequest, event_id: int) -> HttpResponse:
        return render(request, 'pages/widget.html', self.context)
