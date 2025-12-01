from django.contrib import admin
from django.urls import path,include
from appEvenements.views import calendar_view
urlpatterns = [
    path('', calendar_view, name='home'),
    path('evenements/', include('appEvenements.urls')),


    
]