from dataclasses import fields
from time import timezone
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView , CreateView, UpdateView, DetailView, DeleteView, TemplateView
from .forms import ClubForm, DemandeCreationClubForm
from .models import Club, Demande_creation_club
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import render_to_string
# from weasyprint import HTML  # Optional - requires system libraries
HTML = None
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

# Create your views here.
def simple_view(request):
    return HttpResponse('This is a simple view!')

def home_view(request):
    return render(request, 'home.html')

class HomeView(TemplateView):
    template_name = 'club/list.html'
    context_object_name = 'clubs'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = Club.objects.all()
        return context

# class ClubListView(ListView):
#     model = Club
#     template_name = 'club/list.html'  # Updated to match actual template location
#     context_object_name = 'clubs'
class ClubListView(ListView):
    model = Club
    template_name = 'club/list.html'
    context_object_name = 'clubs'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Récupération des paramètres GET
        search = self.request.GET.get('search')
        date_filter = self.request.GET.get('date')

        # 🔎 Rechercher par nom du club
        if search:
            queryset = queryset.filter(name__icontains=search)

        # 📅 Filtrer par date (ex : année de création)
        if date_filter:
            queryset = queryset.filter(established_date__year=date_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # garder les valeurs sélectionnées
        context['selected_search'] = self.request.GET.get('search', '')
        context['selected_date'] = self.request.GET.get('date', '')

        return context

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
#Demande Creation Club Views

# class DemandeCreationClubView(CreateView):
#     model = Demande_creation_club
#     form_class = DemandeCreationClubForm
#     template_name = 'club/demande_creation_club_form.html'
#     success_url = '/club/demandes/'

class DemandeCreationClubView(CreateView):
    model = Demande_creation_club
    form_class = DemandeCreationClubForm
    template_name = 'club/demande_creation_club_form.html'
    success_url = '/club/demandes/'

    def form_valid(self, form):
        # 1) Sauvegarde du formulaire
        self.object = form.save()

        # 2) Récupérer les données propres du formulaire
        club_name = form.cleaned_data.get('club_name')
        email = form.cleaned_data.get('emailResponsable')
        email_club = form.cleaned_data.get('emailClub')
        president_name = form.cleaned_data.get('president_name')
        vice_president_name = form.cleaned_data.get('vice_president_name')
        requested_by = form.cleaned_data.get('requested_by')
        
        # 3) Générer le HTML pour le PDF
        html_string = render_to_string(
    'club/pdf_template.html',
    {
        'club_name': club_name,
        'email': email,  # correspond au template
        'email_club': email_club,
        'president_name': president_name,
        'vice_president_name': vice_president_name,
        'requested_by': requested_by
    }
)

        # 4) Générer le PDF
        pdf = HTML(string=html_string).write_pdf()

        # 5) Retourner le PDF en réponse HTTP (téléchargement)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="extrait.pdf"'
        
        return response

class DemandeListView(ListView):
    model = Demande_creation_club
    template_name = 'club/demande_creation_club_list.html'  # Updated to match actual template location
    context_object_name = 'demandes'

class DemandeCreationClubDetailView(DetailView):
    model = Demande_creation_club
    template_name = 'club/demande_creation_club_detail.html'

class DemandeCreationClubUpdateView(UpdateView):
    model = Demande_creation_club
    form_class = DemandeCreationClubForm
    template_name = 'club/demande_creation_club_form.html'
    success_url = '/club/demandes/'

class DemandeCreationClubDeleteView(DeleteView):
    model = Demande_creation_club
    template_name = 'club/demande_creation_club_confirm_delete.html'
    success_url = '/club/demandes/'
    def test_func(self):
        return self.request.user.role == 'committee' or self.request.user.is_superuser

# admin views for demande_creation_club can be added similarly

class DemandeCreationClubAdminListView(ListView):
    model = Demande_creation_club
    template_name = 'club/demande_creation_club_admin_list.html'
    context_object_name = 'demandes_admin'

    
def accept_demande(request, demande_id):
    demande = get_object_or_404(Demande_creation_club, demande_id=demande_id)

    # Création automatique du club
    Club.objects.create(
        name=demande.club_name,
        description=demande.club_description,
        established_date=timezone.now().date()  # ou une date demandée
    )

    # Option : Supprimer la demande ou la marquer comme traitée
    demande.delete()

    messages.success(request, "Le club a été créé avec succès !")
    return redirect('club_list_view')

class ClubListAdminView(ListView):
    model = Club
    template_name = 'club/clublistadmin.html'
    context_object_name = 'clubs'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Récupération des paramètres GET
        search = self.request.GET.get('search')
        date_filter = self.request.GET.get('date')

        # 🔎 Rechercher par nom du club
        if search:
            queryset = queryset.filter(name__icontains=search)

        # 📅 Filtrer par date (ex : année de création)
        if date_filter:
            queryset = queryset.filter(established_date__year=date_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # garder les valeurs sélectionnées
        context['selected_search'] = self.request.GET.get('search', '')
        context['selected_date'] = self.request.GET.get('date', '')

        return context
