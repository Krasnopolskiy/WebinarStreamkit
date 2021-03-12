from django.contrib.auth import forms as auth_forms
from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from PIL import Image
import os
from pathlib import Path
from main.models import User
from webinar_streamkit.settings import BASE_DIR
from . import forms
from main.forms import ImageForm, ApikeyForm


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class ProfileView(View):
    context = {'pagename': 'Profile'}
    form = ImageForm()
    # context["imguploadformm"] = form

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        self.context['userinfo'] = User.objects.get(username=request.user.username)
        self.context['apikey'] = User.objects.get(username=request.user.username).apikey
        if not self.context['apikey']:
            self.context['apikey'] = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        return render(request, 'pages/profile.html', self.context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            user = User.objects.get(username=request.user.username)
            original_image = Image.open(os.getcwd()+img_obj.image.url)
            size = (200, 200)
            resized_image = original_image.resize(size)
            resized_image.save(os.getcwd()+img_obj.image.url)
            user.avatar = img_obj.image.url
            user.save()
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        self.context['userinfo'] = User.objects.get(username=request.user.username)

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
