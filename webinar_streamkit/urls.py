from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import path, reverse_lazy
from django_registration.backends.one_step.views import RegistrationView

from main.consumers import ChatConsumer
from main.forms import ExtendedSignupForm
from main.views import (EventView, IndexView, ProfileView, ScheduleView, UserInformationView,
                        WebinarCredentialsView)

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('login/', LoginView.as_view(
        template_name='registration/login.html',
        extra_context={'pagename': 'Авторизация'},
    ), name='login'),
    path('signup/', RegistrationView.as_view(
        template_name='registration/signup.html',
        extra_context={'pagename': 'Регистрация'},
        form_class=ExtendedSignupForm,
        success_url=reverse_lazy('index')
    ), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', IndexView.as_view(), name='index'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/password', PasswordChangeView.as_view(
        success_url=reverse_lazy('profile')
    ), name='change_password'),
    path('profile/webinar/credentials', WebinarCredentialsView.as_view(), name='update_webinar_credentials'),
    path('profile/user/information', UserInformationView.as_view(), name='update_user_information'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    path('event/<int:event_id>', EventView.as_view(), name='event')
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )


websocket_urlpatterns = [
    path('chat/<int:id>/', ChatConsumer.as_asgi())
]
