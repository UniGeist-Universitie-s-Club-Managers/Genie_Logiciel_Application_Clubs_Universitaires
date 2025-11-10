from django.shortcuts import render
from .models import Evenement
from django.views import *
from django.views.generic import *
from .forms import EvenementForm
# Create your views here.
class ListeEvenementsView(ListView):
    model = Evenement
    template_name = 'appEvenements/evenements_list.html'
    context_object_name = 'evenements'
    paginate_by = 10
class DetailEvenementView(DetailView):
    model = Evenement
    template_name = 'appEvenements/evenements_details.html'
    context_object_name = 'evenement'
    pk_url_kwarg = 'evenement_id'
class CreateEvenementView(CreateView):
    model = Evenement
    form_class = EvenementForm
    template_name = 'appEvenements/evenements_form.html'
    success_url = '/evenements/liste/'

class UpdateEvenementView(UpdateView):
    model = Evenement
    form_class = EvenementForm
    template_name = 'appEvenements/evenements_form.html'
    pk_url_kwarg = 'evenement_id'
    success_url = '/evenements/liste/'

class DeleteEvenementView(DeleteView):
    model = Evenement
    template_name = 'appEvenements/confirm_delete.html'
    pk_url_kwarg = 'evenement_id'
    success_url = '/evenements/liste/'
    failure_url = '/evenements/liste/'
