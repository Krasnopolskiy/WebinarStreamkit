import requests
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from main.models import DBModel
from main.models import User
from main.forms import SignupForm, WebinarForm
from . import forms
from main.forms import ImageForm, ApikeyForm
from datetime import datetime
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
        if 'error' not in data.keys():
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
    model = DBModel()

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        self.context['userinfo'] = self.model.get_user(request.user.username)
        self.context['apikey'] = self.model.get_apikey(request.user.username)
        self.context['webinar_form'] = forms.WebinarForm()
        if not self.context['apikey']:
            self.context['apikey'] = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        return render(request, 'pages/profile.html', self.context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            self.model.set_avatar(img_obj, request.user.username)
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        self.context['userinfo'] = self.model.get_user(request.user.username)
        self.context['webinar_form'] = forms.WebinarForm()

        api_key_form = ApikeyForm(request.POST)
        webinar_form = WebinarForm(request.POST)
        self.context['apikey'] = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        user = self.context['userinfo']
        if api_key_form.is_valid() and len(request.POST.get('apikey')) == 32:
            self.model.set_apikey(request.POST.get('apikey'), request.user.username)
            self.context['apikey'] = request.POST.get('apikey')
            user.apikey = request.POST.get('apikey')
            user.save()

        if webinar_form.is_valid():
            self.model.set_webinar_account(request.POST.get('webinar_email'),
                                           request.POST.get('webinar_password'),
                                           request.user.username)

        return render(request, 'pages/profile.html', self.context)


class EventView(View):
    context = {'pagename': 'Event'}

    def get(self, request: HttpRequest, event_id) -> HttpResponse:
        session = requests.Session()
        session.post('https://events.webinar.ru/api/login',
                     data={'email': request.user.webinar_email, 'password': request.user.webinar_password})
        data = session.get(f'https://events.webinar.ru/api/event/{event_id}').json()
        print(data['eventSessions'])
        self.context['name'] = data['name']
        self.context['startsAt'] = datetime.strptime(data['startsAt'], '%Y-%m-%dT%H:%M:%S%z')
        self.context['org_name'] = data['organization']['name']
        self.context['status'] = data['status']
        self.context['sessionId'] = event_id
        self.context['userId'] = data['createUser']['id']
        self.context['webinarId'] = data['eventSessions'][0]['id']

        return render(request, 'pages/event.html', self.context)


class ScheduleView(View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        session = requests.Session()
        session.post('https://events.webinar.ru/api/login', data={'email': request.user.webinar_email,
                                                                  'password': request.user.webinar_password})
        url = 'https://events.webinar.ru/api/organizations/' + str(request.user.organizationId) + \
              '/eventsessions/list/planned'
        events = session.get(url)
        events = json.loads(events.text)
        print(events)
        if 'error' not in events:
            print(session.get('https://events.webinar.ru//api/event/session/8455019/participations').text)
            self.context['events'] = events
        return render(request, 'pages/schedule.html', self.context)


class WidgetView(View):
    context = {'pagename': 'Widget'}

    def get(self, request: HttpRequest, input_id: int) -> HttpResponse:
        session = requests.Session()

        session.post('https://events.webinar.ru/api/login',
                     data={'email': request.user.webinar_email, 'password': request.user.webinar_password})

        data = session.get(f'https://events.webinar.ru/api/event/{input_id}').json()
        sessionId = data['eventSessions'][0]['id']
        self.context['answer'] = json.loads(session.get(f'https://events.webinar.ru/api/eventsessions/{sessionId}/chat').text)
        self.context['chat'] = []
        self.context['awaiting_msgs'] = []

        for item in self.context['answer']:
            if not item['isModerated']:
                self.context['awaiting_msgs'].append(item)
            elif not item['isDeleted']:
                self.context['chat'].append(item)

        return render(request, 'pages/chat_widget.html', self.context)
