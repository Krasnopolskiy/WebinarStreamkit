from django.shortcuts import render
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View
from . import forms

class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)

class SignupView(View):
    context = {'pagename': 'Signup'}

    def get(self, request: HttpRequest) -> HttpResponse:
        self.context['form'] = forms.SignUpForm()
        return render(request, 'registration/signup.html', self.context)
