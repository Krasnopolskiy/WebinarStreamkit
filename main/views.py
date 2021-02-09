from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View

from . import forms


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class LogInView(View):
    context = {'pagename': 'Login'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['form'] = forms.LoginForm()
        return render(request, 'registration/login.html', self.context)
