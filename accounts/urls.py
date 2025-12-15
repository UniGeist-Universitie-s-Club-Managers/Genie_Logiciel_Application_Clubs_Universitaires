# accounts/urls.py
from django.urls import path

from appEvenements.views import ListeEvenementsView
from resources.views import ResourceListView, AidListView
from clubApp.views import ClubListAdminView, ClubListView, DemandeListView
from . import views



urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_view, name='dashboard'),

    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),



    # Profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    path('delete/', views.delete_account, name='delete_account'),

    # Historique utilisateur (adhésions, contributions, badges)
    path('history/', views.history_view, name='user_history'),

    path('club/demandes/', DemandeListView.as_view(), name='demande_list_view'),
    path('club/clublist/', ClubListAdminView.as_view(), name='club_list_admin_view'),

    # Chatbot
    path('chatbot/', views.chatbot_view, name='chatbot'),

    # Home pages
    #path('clubs-home/', views.clubs_home_view, name='clubs_home'),
    path('list/', ClubListView.as_view(), name='club_list_view'),
    path('liste/', ListeEvenementsView.as_view(), name='liste'),
    path("", ResourceListView.as_view(), name="resource_list"),
    path("aids/", AidListView.as_view(), name="aid_list"),
    path('events-home/', views.events_home_view, name='events_home'),
    path('forums-home/', views.forums_home_view, name='forums_home'),
    path('resources-home/', views.resources_home_view, name='resources_home'),
    path('help-home/', views.help_home_view, name='help_home'),

]
