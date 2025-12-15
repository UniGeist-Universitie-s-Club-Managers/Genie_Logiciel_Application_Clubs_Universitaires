"""
URL configuration for university_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from accounts.views import admin_panel, admin_accounts, admin_events, admin_forums, admin_resources, admin_aids, admin_clubs, admin_surveys, admin_threads
from accounts.views import admin_panel

urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/clubs-home/', permanent=False), name='home'),
    path('admin/', admin_panel, name='admin_panel'),
    path('admin/accounts/', admin_accounts, name='admin_accounts'),
    path('admin/events/', admin_events, name='admin_events'),
    path('admin/forums/', admin_forums, name='admin_forums'),
    path('admin/resources/', admin_resources, name='admin_resources'),
    path('admin/aids/', admin_aids, name='admin_aids'),
    path('admin/clubs/', admin_clubs, name='admin_clubs'),
    path('admin/surveys/', admin_surveys, name='admin_surveys'),
    path('admin/threads/', admin_threads, name='admin_threads'),
    path('django-admin/', admin.site.urls),  # Django's admin moved to /django-admin/
    path('club/', include('clubApp.urls')),
    path('evenements/', include('appEvenements.urls')),
    path('resources/', include('resources.urls')),
    path('accounts/', include('accounts.urls')),
    path('forum/', include('forums.forum.urls', namespace='forum')),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
