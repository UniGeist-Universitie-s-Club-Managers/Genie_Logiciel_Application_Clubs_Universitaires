from django.urls import path
from .views import *

urlpatterns = [
    path('', simple_view, name='club_simple_view'),
    path('home/', home_view, name='club_home_view'),
    path('list/', ClubListView.as_view(), name='club_list_view'),
    path('add/', ClubCreateView.as_view(), name='club_add_view'),
    path('update/<int:pk>/', ClubUpdateView.as_view(), name='club_update_view'),
    path('detail/<int:pk>/', DetailView.as_view(), name='club_detail_view'),
    path('delete/<int:pk>/', DeleteView.as_view(), name='club_delete_view'),

]
