from django.contrib.auth import forms as auth_forms
from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from main.models import User
from . import forms
from main.forms import ImageForm, ApikeyForm
from datetime import datetime
import requests, json


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
    sessionid='6c4221eb82804f97a6b6e27c7a005ee5'

    def get(self, request: HttpRequest) -> HttpResponse:
        information = requests.get('https://events.webinar.ru/api/eventsession/8454775').json()
        self.context['name'] = information['name']
        self.context['startsAt'] = datetime.strptime(information['startsAt'], '%d.%m.%y %H:%M')
        self.context['org_name'] = information['organization']['name']
        self.context['status'] = information['status']

        return render(request, 'pages/event.html', self.context)


class ScheduleView(View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        session = requests.Session()
        session.post('https://events.webinar.ru/api/login', data={'email': request.user.service_email, 'password': request.user.service_password})
        data = json.loads(session.get('https://events.webinar.ru/api/login').text)
        organization_id = data['memberships'][0]['organization']['id']
        url = 'https://events.webinar.ru/api/organizations/' + str(organization_id) + '/eventsessions/list/planned'
        events = session.get(url)
        self.context['events'] = json.loads(events.text)
        return render(request, 'pages/schedule.html', self.context)
