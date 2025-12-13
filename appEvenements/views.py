from django.shortcuts import render, redirect, get_object_or_404
from .models import Evenement, Participation
from django.views import *
from django.views.generic import *
from .forms import EvenementForm, PromotionForm
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from accounts.models import Membership
from django.urls import reverse
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
except ImportError:
    canvas = None
from io import BytesIO
import datetime
from django.contrib import messages

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evenement = self.get_object()
        user = self.request.user
        is_admin_or_member = user.is_superuser or user.is_staff or Membership.objects.filter(user=user, active=True).exists()
        context['is_admin_or_member'] = is_admin_or_member
        if is_admin_or_member:
            context['participants'] = Participation.objects.filter(evenement=evenement).select_related('user')
        context['is_registered'] = Participation.objects.filter(evenement=evenement, user=user).exists() if user.is_authenticated else False
        context['is_full'] = Participation.objects.filter(evenement=evenement).count() >= evenement.max_participants
        return context

class CreateEvenementView(LoginRequiredMixin, CreateView):
    model = Evenement
    form_class = EvenementForm
    template_name = 'appEvenements/evenements_form.html'
    success_url = '/evenements/liste/'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        print(f"Dispatch: user authenticated: {user.is_authenticated}")
        if not user.is_authenticated:
            messages.info(request, "Vous devez vous connecter pour créer un événement.")
            return redirect(f'/accounts/login/?next={request.path}')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        print(f"Form valid called, user: {user}, is_superuser: {user.is_superuser}, is_staff: {user.is_staff}")
        has_membership = Membership.objects.filter(user=user, active=True).exists()
        print(f"Has active membership: {has_membership}")
        if not (user.is_superuser or user.is_staff or has_membership):
            print("No permission, returning form_invalid")
            messages.error(self.request, "Vous devez être administrateur ou membre d'un groupe pour créer un événement.")
            return self.form_invalid(form)
        print("Has permission, calling super().form_valid")
        result = super().form_valid(form)
        print("Form saved successfully, redirecting")
        return result

    def form_invalid(self, form):
        print(f"Form invalid, errors: {form.errors}")
        print(f"Non field errors: {form.non_field_errors()}")
        return super().form_invalid(form)

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

class AdminInterfaceView(LoginRequiredMixin, ListView):
    model = Evenement
    template_name = 'appEvenements/admin_interface.html'
    context_object_name = 'evenements'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_superuser or user.is_staff or Membership.objects.filter(user=user, active=True).exists()):
            messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")
            return redirect('liste')
        return super().dispatch(request, *args, **kwargs)

def download_pdf(request, evenement_id):
    evenement = Evenement.objects.get(id=evenement_id)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Titre
    title = Paragraph(f"Détails de l'événement: {evenement.titre}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Détails
    details = [
        f"Description: {evenement.description}",
        f"Date de début: {evenement.date_debut.strftime('%d/%m/%Y %H:%M')}",
        f"Date de fin: {evenement.date_fin.strftime('%d/%m/%Y %H:%M')}",
        f"Lieu: {evenement.lieu}",
        f"Statut: {evenement.get_statut_display()}",
        f"Visibilité: {evenement.get_visibilite_display()}",
        f"Durée: {evenement.get_duree()}",
    ]

    for detail in details:
        p = Paragraph(detail, styles['Normal'])
        story.append(p)
        story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{evenement.titre}.pdf"'
    return response





def calendar_view(request):
    # Get upcoming events closest to current date
    from django.utils import timezone
    now = timezone.now()
    upcoming_events = Evenement.objects.filter(date_debut__gte=now).order_by('date_debut')[:10]

    # Get featured events for homepage (all public events that are marked as featured, including past ones)
    featured_events = Evenement.objects.filter(visibilite='public', featured=True).order_by('-date_debut')[:6]

    # Get statistics
    total_events = Evenement.objects.count()
    upcoming_events_count = Evenement.objects.filter(date_debut__gte=now).count()
    active_events = Evenement.objects.filter(statut='en_cours').count()
    completed_events = Evenement.objects.filter(statut='termine').count()

    events_data = []
    for event in upcoming_events:
        events_data.append({
            'id': event.id,
            'title': event.titre,
            'start': event.date_debut.isoformat(),
            'end': event.date_fin.isoformat(),
            'description': event.description,
            'location': event.lieu,
            'status': event.statut,
        })

    context = {
        'events': events_data,
        'featured_events': featured_events,
        'total_events': total_events,
        'upcoming_events': upcoming_events_count,
        'active_events': active_events,
        'completed_events': completed_events,
    }

    # Check if this is a homepage request or calendar request
    if request.path in ['/', '/evenements/']:
        return render(request, 'home.html', context)
    else:
            return render(request, 'appEvenements/calendar.html', context)

def promote_event(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)

    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES, instance=evenement)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'événement '{evenement.titre}' a été mis à la une avec succès !")
            return redirect('admin_interface')
    else:
        form = PromotionForm(instance=evenement)

    return render(request, 'appEvenements/promotion_form.html', {
        'form': form,
        'evenement': evenement
    })

def remove_promotion(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)
    evenement.featured = False
    evenement.promotion_image = None
    evenement.promotion_description = None
    evenement.save()
    messages.success(request, f"La promotion de l'événement '{evenement.titre}' a été supprimée.")
    return redirect('admin_interface')

def toggle_featured(request, evenement_id):
    if request.method == 'POST':
        try:
            event = Evenement.objects.get(id=evenement_id)
            event.featured = not event.featured
            event.save()
            messages.success(request, f"L'événement '{event.titre}' a été {'ajouté aux' if event.featured else 'retiré des'} événements à la une.")
        except Evenement.DoesNotExist:
            messages.error(request, "Événement non trouvé.")
    return redirect('home')

def register_evenement(request, evenement_id):
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour vous inscrire à un événement.")
        return redirect('login')

    evenement = get_object_or_404(Evenement, id=evenement_id)
    user = request.user

    # Check if already registered
    if Participation.objects.filter(evenement=evenement, user=user).exists():
        messages.warning(request, "Vous êtes déjà inscrit à cet événement.")
        return redirect('detail_evenement', evenement_id=evenement_id)

    # Check if event is full
    if Participation.objects.filter(evenement=evenement).count() >= evenement.max_participants:
        messages.error(request, "L'événement est complet.")
        return redirect('detail_evenement', evenement_id=evenement_id)

    # Create participation
    Participation.objects.create(evenement=evenement, user=user)
    messages.success(request, f"Vous vous êtes inscrit avec succès à l'événement '{evenement.titre}'.")
    return redirect('detail_evenement', evenement_id=evenement_id)
