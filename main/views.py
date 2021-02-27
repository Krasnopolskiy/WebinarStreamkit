from django.contrib.auth import forms as auth_forms
from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from main.models import User
from . import forms
from main.forms import ImageForm, ApikeyForm


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class ProfileView(View):
    context = {'pagename': 'Profile'}
    form = ImageForm()

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['password_form'] = auth_forms.PasswordChangeForm(user=request.user)
        self.context['apikey_form'] = forms.ApikeyForm()
        userinfo = User.objects.get(username=request.user.username)
        if userinfo.avatar=="":
            self.context["hasavatar"] = False
        else:
            self.context["hasavatar"] = True

        self.context['apikey'] = userinfo.apikey

        self.context["userinfo"] = userinfo
        self.context["imguploadformm"] = self.form
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
        userinfo = User.objects.get(username=request.user.username)
        if userinfo.avatar == "":
            self.context["hasavatar"] = False
        else:
            self.context["hasavatar"] = True

        api_key_form = ApikeyForm(request.POST)
        self.context['apikey'] = ''
        if api_key_form.is_valid():
            user = User.objects.get(username=request.user.username)
            user.apikey = request.POST.get('apikey')
            user.save()
            self.context['apikey'] = user.apikey

        self.context["userinfo"] = userinfo
        self.context["imguploadformm"] = self.form
        return render(request, 'pages/profile.html', self.context)


class ScheduleView(View):
    context = {'pagename': 'Schedule'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/schedule.html', self.context)
