from django.contrib import admin
from django.contrib.auth.views import LoginView, PasswordChangeView, LogoutView
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
    path('signup/', views.AdvRegistrationView.as_view(), name='signup'),
    path('change-password/', PasswordChangeView.as_view(), name='change_password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.IndexView.as_view(), name='index'),
    path('event/', views.EventView.as_view(), name='event'),
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
    path('chat/', views.ChatView.as_view(), name='chat'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
