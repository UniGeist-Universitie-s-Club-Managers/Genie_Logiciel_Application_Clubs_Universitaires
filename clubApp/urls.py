from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('simple/', simple_view, name='club_simple_view'),
    path('home/', home_view, name='club_home_view'),
    path('list/', ClubListView.as_view(), name='club_list_view'),
    path('add/', ClubCreateView.as_view(), name='club_add_view'),
    path('update/<int:pk>/', ClubUpdateView.as_view(), name='club_update_view'),
    path('detail/<int:pk>/', DetailView.as_view(), name='club_detail_view'),
    path('delete/<int:pk>/', DeleteView.as_view(), name='club_delete_view'),
    
    #demande creation club urls
    
    path('demande_creation/', DemandeCreationClubView.as_view(), name='demande_creation_club_view'),
    path('demandes/', DemandeListView.as_view(), name='demande_list_view'),
    path('demande/<int:pk>/', DemandeCreationClubDetailView.as_view(), name='demande_creation_club_detail_view'),
    path('demande/update/<int:pk>/', DemandeCreationClubUpdateView.as_view(), name='demande_creation_club_update_view'),
    path('demande/delete/<int:pk>/', DemandeCreationClubDeleteView.as_view(), name='demande_creation_club_delete_view'),
    path('admin/demandes/', DemandeCreationClubAdminListView.as_view(), name='demande_creation_club_admin_list_view'),
    path('demandes/accept/<int:demande_id>/', accept_demande, name='accept_demande'),


]
