import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.urls import path, reverse_lazy, include

from main.consumers import (AwaitingMessagesConsumer, ChatConsumer,
                            ControlConsumer)
from main.forms import ExtendedRegistrationForm
from main.views import (AwaitingMessagesView, ChatView, ControlView, EventView,
                        ExtendedLoginView, ExtendedRegistrationView, IndexView,
                        ProfileView, ScheduleView, UserInformationView,
                        WebinarCredentialsView)

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('login/', ExtendedLoginView.as_view(
        template_name='registration/login.html',
        extra_context={'pagename': 'Авторизация'},
    ), name='login'),
    path('signup/', ExtendedRegistrationView.as_view(
        template_name='registration/signup.html',
        extra_context={'pagename': 'Регистрация'},
        form_class=ExtendedRegistrationForm,
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
    path('event/<int:event_id>', EventView.as_view(), name='event'),
    path('event/<int:event_id>/chat', ChatView.as_view(), name='chat'),
    path('event/<int:event_id>/awaiting', AwaitingMessagesView.as_view(), name='awaiting'),
    path('event/<int:event_id>/control', ControlView.as_view(), name='control')
]


if settings.DEBUG:
    urlpatterns = [
        path('__debag__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )


websocket_urlpatterns = [
    path('event/<int:event_id>/chat', ChatConsumer.as_asgi()),
    path('event/<int:event_id>/awaiting', AwaitingMessagesConsumer.as_asgi()),
    path('event/<int:event_id>/control', ControlConsumer.as_asgi()),
]
