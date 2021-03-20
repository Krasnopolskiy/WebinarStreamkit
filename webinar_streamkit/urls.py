from django.contrib import admin
from django.contrib.auth.views import LoginView, PasswordChangeView, LogoutView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('login/', LoginView.as_view(
        template_name='registration/login.html',
        extra_context={'pagename': 'Авторизация'},

    ), name='login'),
    path('signup/', views.AdvRegistrationView.as_view(), name='signup'),
    path('change-password/', login_required(PasswordChangeView.as_view()), name='change_password'),
    path('profile/', login_required(views.ProfileView.as_view()), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.IndexView.as_view(), name='index'),
    path('event/<int:event_id>/', login_required(views.EventView.as_view()), name='event'),
    path('schedule/', login_required(views.ScheduleView.as_view()), name='schedule'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
