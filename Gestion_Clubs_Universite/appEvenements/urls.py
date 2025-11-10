from django.contrib import admin
from django.urls import path,include
from .views import ListeEvenementsView, DetailEvenementView, CreateEvenementView, UpdateEvenementView, DeleteEvenementView

urlpatterns = [
    path('evenements/',ListeEvenementsView.as_view(), name='evenements'),
    path('liste/', ListeEvenementsView.as_view(), name='liste'),
    path('detail/<int:evenement_id>/', DetailEvenementView.as_view(), name='details'),
    path('creer/', CreateEvenementView.as_view(), name='ajouter'),
    path('modifier/<int:evenement_id>/', UpdateEvenementView.as_view(), name='modifier'),
    path('supprimer/<int:evenement_id>/', DeleteEvenementView.as_view(), name='annuler'),
]
