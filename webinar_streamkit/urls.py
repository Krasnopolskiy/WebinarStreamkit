from django.contrib import admin
from django.contrib.auth.views import LoginView, PasswordChangeView, LogoutView
from django_registration.backends.one_step.views import RegistrationView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('login/', LoginView.as_view(
        template_name='registration/login.html',
        extra_context={'pagename': 'Авторизация'},

    ), name='login'),
    path('signup/', RegistrationView.as_view(
        template_name='registration/signup.html',
        extra_context={'pagename': 'Регистрация'},
        success_url='/',
    ), name='signup'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.IndexView.as_view(), name='index'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
