from audioop import reverse

from django.contrib.auth import get_user_model, authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views import View

from . import forms


class IndexView(View):
    context = {'pagename': 'Index'}

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, 'pages/index.html', self.context)


class LoginView(View):
    context = {'pagename': 'signin'}

    def get(self, request):
        self.context['form'] = forms.LoginView()
        return render(request, 'registration/login.html', self.context)

    def post(self, request):
        get_user_model()
        form = forms.LoginView(request.POST)
        self.context['form'] = form
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('index'))
        return render(request, 'registration/login.html', self.context)

