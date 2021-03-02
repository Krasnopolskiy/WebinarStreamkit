from django.contrib.auth import forms as auth_forms
from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View

from . import forms


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class ProfileView(View):
    context = {'pagename': 'Profile'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        return render(request, 'pages/profile.html', self.context)

class EventView(View):
    context = {'pagename': 'Event'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'main/event.html', self.context)

class ScheduleView(View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/schedule.html', self.context)
