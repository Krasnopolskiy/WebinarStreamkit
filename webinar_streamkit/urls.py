from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from main import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('change-password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.IndexView.as_view(), name='index'),
]
