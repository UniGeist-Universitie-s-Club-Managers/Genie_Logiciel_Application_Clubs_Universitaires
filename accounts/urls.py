# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_view, name='dashboard'),

    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Vérification email
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),

    # Profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    path('delete/', views.delete_account, name='delete_account'),

    # Historique utilisateur (adhésions, contributions, badges)
    path('history/', views.history_view, name='user_history'),

    # Chatbot
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('verify/success/', views.fake_verify_success, name='fake_verify_success'),

]
