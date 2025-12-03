from django.urls import path

from . import views


app_name = "resources"


urlpatterns = [
    # Resources
    path("", views.ResourceListView.as_view(), name="resource_list"),
    path("resources/add/", views.ResourceCreateView.as_view(), name="resource_create"),
    path("resources/export-pdf/", views.export_resources_pdf, name="export_resources_pdf"),
    path("resources/<int:pk>/favorite/", views.toggle_favorite_resource, name="resource_favorite"),
    path("resources/<int:pk>/", views.ResourceDetailView.as_view(), name="resource_detail"),
    path("resources/<int:pk>/edit/", views.ResourceUpdateView.as_view(), name="resource_update"),
    path("resources/<int:pk>/delete/", views.ResourceDeleteView.as_view(), name="resource_delete"),
    path("resources/<int:pk>/validate/", views.ResourceValidateView.as_view(), name="resource_validate"),
    path("resources/<int:pk>/reject/", views.ResourceRejectView.as_view(), name="resource_reject"),

    # Aids
    path("aids/", views.AidListView.as_view(), name="aid_list"),
    path("aids/add/", views.AidCreateView.as_view(), name="aid_create"),
    path("aids/export-pdf/", views.export_aids_pdf, name="export_aids_pdf"),
    path("aids/<int:pk>/favorite/", views.toggle_favorite_aid, name="aid_favorite"),
    path("aids/<int:pk>/", views.AidDetailView.as_view(), name="aid_detail"),
    path("aids/<int:pk>/edit/", views.AidUpdateView.as_view(), name="aid_update"),
    path("aids/<int:pk>/delete/", views.AidDeleteView.as_view(), name="aid_delete"),
    path("aids/<int:pk>/validate/", views.AidValidateView.as_view(), name="aid_validate"),
    path("aids/<int:pk>/reject/", views.AidRejectView.as_view(), name="aid_reject"),

    # Aid Requests
    path("requests/", views.AidRequestListView.as_view(), name="aidrequest_list"),
    path("requests/add/", views.AidRequestCreateView.as_view(), name="aidrequest_create"),
    path("requests/<int:pk>/approve/", views.RequestApproveView.as_view(), name="request_approve"),
    path("requests/<int:pk>/reject/", views.RequestRejectView.as_view(), name="request_reject"),

    # Favorites
    path("favorites/", views.FavoriteListView.as_view(), name="favorites_list"),

    # Home
    path("", views.home, name="home"),
    # Note: admin_dashboard est maintenant défini dans se_crud/urls.py pour éviter le catch-all de Django admin
]
