# forum/urls.py
from django.urls import path
from . import views
from .views import (
    SurveyListView,
    SurveyDetailView,
    SurveyCreateView,
    SurveyUpdateView,
    SurveyDeleteView,
    survey_vote
)


app_name = 'forum'

urlpatterns = [
    # Page d'accueil - Liste des threads
    path('', views.ThreadListView.as_view(), name='thread-list'),
    
    # Forum URLs (US 9.1, 9.2, 7.3)
    path('forums/', views.ForumListView.as_view(), name='forum-list'),
    path('forum/<int:pk>/', views.ForumDetailView.as_view(), name='forum-detail'),
    path('forum/new/', views.ForumCreateView.as_view(), name='forum-create'),
    path('forum/<int:pk>/edit/', views.ForumUpdateView.as_view(), name='forum-update'),
    path('forum/<int:pk>/delete/', views.ForumDeleteView.as_view(), name='forum-delete'),
    
    # Thread URLs (US 10.1)
    path('thread/<int:pk>/', views.ThreadDetailView.as_view(), name='thread-detail'),
    path('thread/new/', views.ThreadCreateView.as_view(), name='thread-create'),
    path('thread/<int:pk>/edit/', views.ThreadUpdateView.as_view(), name='thread-update'),
    path('thread/<int:pk>/delete/', views.ThreadDeleteView.as_view(), name='thread-delete'),
    
    # Post (réponse) URLs (US 10.3, 11.2, 11.3, 11.4)
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    
    # Survey (sondage) URLs (US 10.2)
    path('surveys/', views.SurveyListView.as_view(), name='survey-list'),
    path('survey/<int:pk>/', views.SurveyDetailView.as_view(), name='survey-detail'),
    path('survey/<int:pk>/vote/', views.survey_vote, name='survey-vote'), 
    path('survey/new/', views.SurveyCreateView.as_view(), name='survey-create'),
    path('survey/<int:pk>/edit/', views.SurveyUpdateView.as_view(), name='survey-update'),
    path('survey/<int:pk>/delete/', views.SurveyDeleteView.as_view(), name='survey-delete'),
]

