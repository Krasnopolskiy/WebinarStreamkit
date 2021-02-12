from django.contrib.auth import get_user_model, authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from django.urls import reverse

from . import forms


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class LoginView(View):
    context = {'pagename': 'Login'}

    def get(self, request):
        self.context['form'] = forms.LoginForm()
        self.context['error'] = False
        self.context['form_error'] = False
        return render(request, 'registration/login.html', self.context)

    def post(self, request):
        get_user_model()
        form = forms.LoginForm(request.POST)
        self.context['form'] = form
        self.context['error'] = True
        if form.is_valid():
            self.context['form_error'] = False
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('index'))
        else:
            self.context['form_error'] = True
        return render(request, 'registration/login.html', self.context)


class SignupView(View):
    context = {'pagename': 'Signup'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['form'] = forms.SignupForm()
        return render(request, 'registration/signup.html', self.context)

    def post(self, request: HttpRequest) -> HttpResponse:
        get_user_model()
        form = forms.SignupForm(request.POST)
        self.context['form'] = form
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('index'))
        return render(request, 'registration/signup.html', self.context)
