from django.contrib import admin
from django.urls import path,include
from .views import ListeEvenementsView, DetailEvenementView, CreateEvenementView, UpdateEvenementView, DeleteEvenementView, AdminInterfaceView, calendar_view, download_pdf, toggle_featured, promote_event, remove_promotion, register_evenement, remove_participant

app_name = 'appEvenements'

urlpatterns = [
    path('',calendar_view, name='home'),
    path('evenements/',ListeEvenementsView.as_view(), name='evenements'),
    path('liste/', ListeEvenementsView.as_view(), name='liste'),
    path('detail/<int:evenement_id>/', DetailEvenementView.as_view(), name='details'),
    path('creer/', CreateEvenementView.as_view(), name='ajouter'),
    path('modifier/<int:evenement_id>/', UpdateEvenementView.as_view(), name='modifier'),
    path('supprimer/<int:evenement_id>/', DeleteEvenementView.as_view(), name='annuler'),
    path('admin/', AdminInterfaceView.as_view(), name='admin_interface'),
    path('calendar/', calendar_view, name='calendar'),
    path('download_pdf/<int:evenement_id>/', download_pdf, name='download_pdf'),
    path('toggle_featured/<int:evenement_id>/', toggle_featured, name='toggle_featured'),
    path('post_social/<int:evenement_id>/', promote_event, name='post_social'),
    path('remove_promotion/<int:evenement_id>/', remove_promotion, name='remove_promotion'),
    path('promote/<int:evenement_id>/', promote_event, name='promote'),
    path('register/<int:evenement_id>/', register_evenement, name='register_evenement'),
    path('remove_participant/<int:evenement_id>/<int:user_id>/', remove_participant, name='remove_participant'),
]
