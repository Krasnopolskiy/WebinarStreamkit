from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.IndexView.as_view(), name='index'),
]
