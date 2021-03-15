from django.contrib.auth import forms as auth_forms
from django_registration.backends.one_step.views import RegistrationView
from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from PIL import Image
import os
from pathlib import Path
from main.models import User
from main.forms import SignupForm
from webinar_streamkit.settings import BASE_DIR
from . import forms
from main.forms import ImageForm, ApikeyForm
from django.contrib.auth import authenticate, login
from django_registration import signals
from django_registration.views import RegistrationView as BaseRegistrationView
import requests, json


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class AdvRegistrationView(BaseRegistrationView):
    template_name = 'registration/signup.html'
    extra_context = {'pagename': 'Регистрация'}
    success_url = '/'
    form_class = SignupForm

    def register(self, form):
        new_user = form.save()
        new_user = authenticate(
            **{
                User.USERNAME_FIELD: new_user.get_username(),
                "password": form.cleaned_data["password1"],
            }
        )
        login(self.request, new_user)
        session = requests.Session()
        session.post('https://events.webinar.ru/api/login',
                     data={'email': new_user.webinar_email, 'password': new_user.webinar_password})
        data = json.loads(session.get('https://events.webinar.ru/api/login').text)
        new_user.id = data['id']
        new_user.organizationId = data['memberships'][0]['organization']['id']
        new_user.sessionId = data['sessionId']
        new_user.save()
        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=self.request
        )
        return new_user


class ProfileView(View):
    context = {'pagename': 'Profile'}
    form = ImageForm()

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
        session = requests.Session()
        session.post('https://events.webinar.ru/api/login', data={'email': request.user.webinar_email, 'password': request.user.webinar_password})
        url = 'https://events.webinar.ru/api/organizations/' + str(request.user.organizationId) + '/eventsessions/list/planned'
        events = session.get(url)
        print(events)
        self.context['events'] = json.loads(events.text)
        return render(request, 'pages/schedule.html', self.context)
