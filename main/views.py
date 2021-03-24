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


'''
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
        self.context['webinar_form'] = forms.WebinarForm()
        self.context['userinfo'] = User.objects.get(username=request.user.username)

        api_key_form = ApikeyForm(request.POST)
        webinar_form = WebinarForm(request.POST)
        self.context['apikey'] = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        user = self.context['userinfo']
        if api_key_form.is_valid() and len(request.POST.get('apikey')) == 32:
            user.apikey = request.POST.get('apikey')
            user.save()
            self.context['apikey'] = user.apikey

        if webinar_form.is_valid():
            user.webinar_email = request.POST.get('webinar_email')
            user.webinar_password = request.POST.get('webinar_password')

            session = requests.Session()
            session.post('https://events.webinar.ru/api/login', data={'email': user.webinar_email, 'password': user.webinar_password})
            json_resp = json.loads(session.get('https://events.webinar.ru/api/login').text)
            print(json_resp)
            user.organizationId = json_resp['memberships'][0]['organization']['id']

            user.save()

        return render(request, 'pages/profile.html', self.context)
        
class EventView(View):
    context = {'pagename': 'Event'}

    def get(self, request: HttpRequest, id: int) -> HttpResponse:
        information = requests.get(f'https://events.webinar.ru/api/eventsession/{id}').json()
        self.context['name'] = information['name']
        self.context['startsAt'] = datetime.strptime(information['startsAt'], '%Y-%m-%dT%H:%M:%S%z')
        self.context['org_name'] = information['organization']['name']
        self.context['status'] = information['status']
        self.context['id'] = id

        return render(request, 'pages/event.html', self.context)


class ScheduleView(View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        session = requests.Session()
        session.post('https://events.webinar.ru/api/login', data={'email': request.user.webinar_email,
                                                                  'password': request.user.webinar_password})
        url = 'https://events.webinar.ru/api/organizations/' + str(request.user.organizationId) + '/eventsessions/list/planned'
        events = session.get(url)
        self.context['events'] = json.loads(events.text)
        return render(request, 'pages/schedule.html', self.context)


class WidgetView(View):
    context = {'pagename': 'Widget'}

    def get(self, request: HttpRequest, id: int) -> HttpResponse:
        session = requests.Session()
        session.post('https://events.webinar.ru/api/login',
                     data={'email': request.user.webinar_email, 'password': request.user.webinar_password})
        self.context['answer'] = json.loads(session.get(f'https://events.webinar.ru/api/eventsessions/{id}/chat').text)

        self.context['chat'] = []
        self.context['awaiting_msgs'] = []

        for item in self.context['answer']:
            if not item['isModerated']:
                self.context['awaiting_msgs'].append(item)
            elif not item['isDeleted']:
                self.context['chat'].append(item)

        return render(request, 'pages/chat_widget.html', self.context)
'''
