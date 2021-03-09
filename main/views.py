from django.contrib.auth import forms as auth_forms
from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from main.models import User, DBModel
from . import forms
from main.forms import ImageForm, ApikeyForm


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class ProfileView(View):
    context = {'pagename': 'Profile'}
    form = ImageForm()
    model = DBModel()

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        self.context['userinfo'] = self.model.get_user(request.user.username)
        self.context['apikey'] = self.context['userinfo'].apikey
        if not self.context['apikey']:
            self.context['apikey'] = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        return render(request, 'pages/profile.html', self.context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            user = self.model.get_user(request.user.username)
            user.avatar = img_obj.image.url
            user.save()
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        self.context['userinfo'] = self.model.get_user(request.user.username)

        api_key_form = ApikeyForm(request.POST)
        self.context['apikey'] = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

        if api_key_form.is_valid() and len(request.POST.get('apikey')) == 32:
            user = self.context['userinfo']
            user.apikey = request.POST.get('apikey')
            user.save()
            self.context['apikey'] = user.apikey

        return render(request, 'pages/profile.html', self.context)


class EventView(View):
    context = {'pagename': 'Event'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/event.html', self.context)


class ScheduleView(View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/schedule.html', self.context)
