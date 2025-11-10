from django.contrib import admin
from django.urls import path,include
from appEvenements.views import ListeEvenementsView, DetailEvenementView, CreateEvenementView, UpdateEvenementView, DeleteEvenementView
urlpatterns = [
    path('', ListeEvenementsView.as_view(), name='home'),
    path('evenements/', include('appEvenements.urls')),


    
]