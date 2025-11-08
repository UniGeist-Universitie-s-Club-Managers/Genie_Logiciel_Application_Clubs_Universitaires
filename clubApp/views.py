from dataclasses import fields
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView , CreateView, UpdateView, DetailView, DeleteView
from .forms import ClubForm
from .models import Club
# Create your views here.
def simple_view(request):
    return HttpResponse('This is a simple view!')
def home_view(request):
    return render(request, 'club/home.html')

class ClubListView(ListView):
    model = Club
    template_name = 'club/list.html'  # Updated to match actual template location
    context_object_name = 'clubs'

class ClubCreateView(CreateView):
    model = Club
    form_class = ClubForm
    template_name = 'club/club_form.html'
    success_url = '/club/list/'

class ClubUpdateView(UpdateView):
    model = Club
    form_class = ClubForm
    template_name = 'club/club_form.html'
    success_url = '/club/list/'
    
class DetailView(DetailView):
    model = Club
    form_class = ClubForm
    template_name = 'club/club_detail.html'
    
class DeleteView(DeleteView):
    model = Club
    fiels ="__all__"
    template_name = 'club/club_confirm_delete.html'
    success_url = '/club/list/'
    def test_func(self):
        return self.request.user.role == 'committee' or self.request.user.is_superuser