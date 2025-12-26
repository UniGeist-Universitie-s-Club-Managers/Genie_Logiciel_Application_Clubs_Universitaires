# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

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

    # Chatbot
    path('chatbot/', views.chatbot_view, name='chatbot'),

    # Home pages
    path('clubs-home/', views.clubs_home_view, name='clubs_home'),
    path('events-home/', views.events_home_view, name='events_home'),
    path('forums-home/', views.forums_home_view, name='forums_home'),
    path('resources-home/', views.resources_home_view, name='resources_home'),
    path('help-home/', views.help_home_view, name='help_home'),

    # Admin panel
    path('admin/', views.admin_panel, name='admin_panel'),
    path('admin/accounts/', views.admin_accounts, name='admin_accounts'),
    path('admin/events/', views.admin_events, name='admin_events'),
    path('admin/clubs/', views.admin_clubs, name='admin_clubs'),
    path('admin/forums/', views.admin_forums, name='admin_forums'),
    path('admin/threads/', views.admin_threads, name='admin_threads'),
    path('admin/surveys/', views.admin_surveys, name='admin_surveys'),
    path('admin/resources/', views.admin_resources, name='admin_resources'),
    path('admin/aids/', views.admin_aids, name='admin_aids'),

    # Admin edit/delete URLs
    path('admin/event/<int:pk>/edit/', views.admin_event_edit, name='admin_event_edit'),
    path('admin/event/<int:pk>/delete/', views.admin_event_delete, name='admin_event_delete'),
    path('admin/club/<int:pk>/edit/', views.admin_club_edit, name='admin_club_edit'),
    path('admin/club/<int:pk>/delete/', views.admin_club_delete, name='admin_club_delete'),
    path('admin/forum/<int:pk>/edit/', views.admin_forum_edit, name='admin_forum_edit'),
    path('admin/forum/<int:pk>/delete/', views.admin_forum_delete, name='admin_forum_delete'),
    path('admin/thread/<int:pk>/edit/', views.admin_thread_edit, name='admin_thread_edit'),
    path('admin/thread/<int:pk>/delete/', views.admin_thread_delete, name='admin_thread_delete'),
    path('admin/survey/<int:pk>/edit/', views.admin_survey_edit, name='admin_survey_edit'),
    path('admin/survey/<int:pk>/delete/', views.admin_survey_delete, name='admin_survey_delete'),
    path('admin/resource/<int:pk>/edit/', views.admin_resource_edit, name='admin_resource_edit'),
    path('admin/resource/<int:pk>/delete/', views.admin_resource_delete, name='admin_resource_delete'),
    path('admin/aid/<int:pk>/edit/', views.admin_aid_edit, name='admin_aid_edit'),
    path('admin/aid/<int:pk>/delete/', views.admin_aid_delete, name='admin_aid_delete'),
    path('admin/event/<int:event_id>/participants/', views.admin_event_participants, name='admin_event_participants'),
]
