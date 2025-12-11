from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.db import models
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta, datetime
import calendar
from django.db.models import Count
from django.http import HttpResponse
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
except ImportError:
    A4 = None
from io import BytesIO

from .forms import AidForm, AidRequestForm, ResourceForm
from .models import Aid, AidRequest, Category, Club, Resource, FAQ, Favorite


def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur."""
    return user.is_authenticated and user.is_staff


def is_organizer(user):
    """Vérifie si l'utilisateur est un organisateur."""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name="Organisateur").exists() or user.is_staff


class AdminRequiredMixin(LoginRequiredMixin):
    """Vérifie que l'utilisateur est un administrateur."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not is_admin(request.user):
            raise PermissionDenied("Vous n'avez pas les permissions d'administrateur.")
        return super().dispatch(request, *args, **kwargs)


class OrganizerRequiredMixin(LoginRequiredMixin):
    """Vérifie que l'utilisateur est un organisateur ou un administrateur."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not is_organizer(request.user):
            raise PermissionDenied("Vous n'avez pas les permissions d'organisateur.")
        return super().dispatch(request, *args, **kwargs)


# ============================================================================
# RESOURCE VIEWS
# ============================================================================

class ResourceListView(LoginRequiredMixin, ListView):
    """Liste des ressources - accessible à tous les utilisateurs connectés."""
    model = Resource
    template_name = "resources/resource_list.html"
    context_object_name = "resources"
    paginate_by = 12

    def get_queryset(self):
        """Affiche uniquement les ressources validées pour les membres, toutes pour les admins."""
        queryset = Resource.objects.select_related("category", "club", "submitted_by")
        
        # Filtrer par validation
        if not is_admin(self.request.user):
            queryset = queryset.filter(is_validated=True)
        
        # Recherche par titre (q)
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        
        # Filtre par catégorie
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Filtre par club
        club_filter = self.request.GET.get('club', '')
        if club_filter:
            queryset = queryset.filter(club_id=club_filter)
        
        return queryset.order_by('-date_submitted')
    
    def get_context_data(self, **kwargs):
        """Ajoute les catégories, clubs et les paramètres de recherche au contexte."""
        context = super().get_context_data(**kwargs)
        
        # Liste des catégories pour le filtre
        context['categories'] = Category.objects.all().order_by('name')
        
        # Liste des clubs pour le filtre
        context['clubs'] = Club.objects.all().order_by('name')
        
        # Paramètres de recherche pour pré-remplir le formulaire
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_club'] = self.request.GET.get('club', '')
        
        return context


class ResourceDetailView(LoginRequiredMixin, DetailView):
    """Détail d'une ressource - accessible à tous les utilisateurs connectés."""
    model = Resource
    template_name = "resources/resource_detail.html"
    context_object_name = "resource"

    def get_object(self, queryset=None):
        """Vérifie que l'utilisateur peut voir cette ressource."""
        obj = super().get_object(queryset)
        # Les membres ne peuvent voir que les ressources validées
        if not is_admin(self.request.user) and not obj.is_validated:
            raise PermissionDenied("Cette ressource n'est pas encore validée.")
        return obj
    
    def get_context_data(self, **kwargs):
        """Ajoute l'information si la ressource est en favori."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                resource=self.object
            ).exists()
        else:
            context['is_favorite'] = False
        return context


class ResourceCreateView(OrganizerRequiredMixin, CreateView):
    """Création d'une ressource - pour les organisateurs et admins."""
    model = Resource
    form_class = ResourceForm
    template_name = "resources/resource_form.html"
    success_url = reverse_lazy("resources:resource_list")

    def form_valid(self, form):
        form.instance.submitted_by = self.request.user
        # Les admins créent des ressources validées, les organisateurs non
        form.instance.is_validated = is_admin(self.request.user)
        response = super().form_valid(form)

        if is_admin(self.request.user):
            messages.success(self.request, "Ressource créée avec succès.")
        else:
            messages.success(
                self.request,
                "Votre ressource a été soumise et sera validée par un administrateur."
            )
        return response


class ResourceUpdateView(AdminRequiredMixin, UpdateView):
    """Modification d'une ressource - uniquement pour les administrateurs."""
    model = Resource
    form_class = ResourceForm
    template_name = "resources/resource_form.html"
    success_url = reverse_lazy("resources:resource_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Ressource mise à jour avec succès.")
        return response


class ResourceDeleteView(AdminRequiredMixin, DeleteView):
    """Suppression d'une ressource - uniquement pour les administrateurs."""
    model = Resource
    template_name = "resources/resource_confirm_delete.html"
    success_url = reverse_lazy("resources:resource_list")

    def form_valid(self, form):
        messages.success(self.request, "Ressource supprimée avec succès.")
        return super().form_valid(form)


class ResourceValidateView(AdminRequiredMixin, View):
    """Validation d'une ressource par un administrateur."""
    
    def post(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk)
        resource.is_validated = True
        resource.save()
        messages.success(
            request,
            f"Ressource '{resource.title}' validée. L'utilisateur {resource.submitted_by.username} a été notifié."
        )
        return redirect('resources:resource_list')


class ResourceRejectView(AdminRequiredMixin, DeleteView):
    """Rejet d'une ressource par un administrateur."""
    model = Resource
    template_name = "resources/resource_reject.html"
    success_url = reverse_lazy("resources:resource_list")

    def form_valid(self, form):
        resource = self.get_object()
        submitted_by = resource.submitted_by
        title = resource.title
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Ressource '{title}' rejetée. L'utilisateur {submitted_by.username} a été notifié."
        )
        return response


# ============================================================================
# AID VIEWS
# ============================================================================

class AidListView(LoginRequiredMixin, ListView):
    """Liste des aides - accessible à tous les utilisateurs connectés."""
    model = Aid
    template_name = "resources/aid_list.html"
    context_object_name = "aids"
    paginate_by = 12

    def get_queryset(self):
        """Affiche uniquement les aides validées pour les membres, toutes pour les admins."""
        queryset = Aid.objects.select_related("category", "club", "submitted_by")
        
        # Filtrer par validation
        if not is_admin(self.request.user):
            queryset = queryset.filter(is_validated=True)
        
        # Recherche par titre (q)
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        
        # Filtre par catégorie
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Filtre par club
        club_filter = self.request.GET.get('club', '')
        if club_filter:
            queryset = queryset.filter(club_id=club_filter)
        
        return queryset.order_by('-date_submitted')
    
    def get_context_data(self, **kwargs):
        """Ajoute les catégories, clubs et les paramètres de recherche au contexte."""
        context = super().get_context_data(**kwargs)
        
        # Liste des catégories pour le filtre
        context['categories'] = Category.objects.all().order_by('name')
        
        # Liste des clubs pour le filtre
        context['clubs'] = Club.objects.all().order_by('name')
        
        # Paramètres de recherche pour pré-remplir le formulaire
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_club'] = self.request.GET.get('club', '')
        
        return context


class AidDetailView(LoginRequiredMixin, DetailView):
    """Détail d'une aide - accessible à tous les utilisateurs connectés."""
    model = Aid
    template_name = "resources/aid_detail.html"
    context_object_name = "aid"

    def get_object(self, queryset=None):
        """Vérifie que l'utilisateur peut voir cette aide."""
        obj = super().get_object(queryset)
        # Les membres ne peuvent voir que les aides validées
        if not is_admin(self.request.user) and not obj.is_validated:
            raise PermissionDenied("Cette aide n'est pas encore validée.")
        return obj
    
    def get_context_data(self, **kwargs):
        """Ajoute l'information si l'aide est en favori."""
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                aid=self.object
            ).exists()
        else:
            context['is_favorite'] = False
        return context


class AidCreateView(OrganizerRequiredMixin, CreateView):
    """Création d'une aide - pour les organisateurs et admins."""
    model = Aid
    form_class = AidForm
    template_name = "resources/aid_form.html"
    success_url = reverse_lazy("resources:aid_list")

    def form_valid(self, form):
        form.instance.submitted_by = self.request.user
        # Les admins créent des aides validées, les organisateurs non
        form.instance.is_validated = is_admin(self.request.user)
        response = super().form_valid(form)
        if is_admin(self.request.user):
            messages.success(self.request, "Aide créée avec succès.")
        else:
            messages.success(
                self.request,
                "Votre aide a été soumise et sera validée par un administrateur."
            )
        return response


class AidUpdateView(AdminRequiredMixin, UpdateView):
    """Modification d'une aide - uniquement pour les administrateurs."""
    model = Aid
    form_class = AidForm
    template_name = "resources/aid_form.html"
    success_url = reverse_lazy("resources:aid_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Aide mise à jour avec succès.")
        return response


class AidDeleteView(AdminRequiredMixin, DeleteView):
    """Suppression d'une aide - uniquement pour les administrateurs."""
    model = Aid
    template_name = "resources/aid_confirm_delete.html"
    success_url = reverse_lazy("resources:aid_list")

    def form_valid(self, form):
        messages.success(self.request, "Aide supprimée avec succès.")
        return super().form_valid(form)


class AidValidateView(AdminRequiredMixin, View):
    """Validation d'une aide par un administrateur."""
    
    def post(self, request, pk):
        aid = get_object_or_404(Aid, pk=pk)
        aid.is_validated = True
        aid.save()
        messages.success(
            request,
            f"Aide '{aid.title}' validée. L'utilisateur {aid.submitted_by.username} a été notifié."
        )
        return redirect('resources:aid_list')


class AidRejectView(AdminRequiredMixin, DeleteView):
    """Rejet d'une aide par un administrateur."""
    model = Aid
    template_name = "resources/aid_reject.html"
    success_url = reverse_lazy("resources:aid_list")

    def form_valid(self, form):
        aid = self.get_object()
        submitted_by = aid.submitted_by
        title = aid.title
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Aide '{title}' rejetée. L'utilisateur {submitted_by.username} a été notifié."
        )
        return response


# ============================================================================
# AID REQUEST VIEWS
# ============================================================================

class AidRequestCreateView(LoginRequiredMixin, CreateView):
    """Création d'une demande de ressource ou d'aide - accessible à tous les utilisateurs connectés."""
    model = AidRequest
    form_class = AidRequestForm
    template_name = "resources/aid_request_form.html"
    success_url = reverse_lazy("resources:resource_list")

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Votre demande a été soumise. Un administrateur l'examinera sous peu."
        )
        return response


class AidRequestListView(LoginRequiredMixin, ListView):
    """Liste des demandes - les membres voient leurs propres demandes, les admins voient tout."""
    model = AidRequest
    template_name = "resources/aid_request_list.html"
    context_object_name = "requests"

    def get_queryset(self):
        """Les membres voient leurs propres demandes, les admins voient tout."""
        queryset = AidRequest.objects.select_related("requested_by")
        if is_admin(self.request.user):
            return queryset
        else:
            return queryset.filter(requested_by=self.request.user)


class RequestApproveView(AdminRequiredMixin, View):
    """Approbation d'une demande par un administrateur."""
    
    def post(self, request, pk):
        req = get_object_or_404(AidRequest, pk=pk)
        req.status = 'approved'
        req.save()
        messages.success(
            request,
            f"Demande approuvée. L'utilisateur {req.requested_by.username} a été notifié."
        )
        return redirect('resources:aidrequest_list')


class RequestRejectView(AdminRequiredMixin, View):
    """Rejet d'une demande par un administrateur."""
    
    def post(self, request, pk):
        req = get_object_or_404(AidRequest, pk=pk)
        req.status = 'rejected'
        req.save()
        messages.success(
            request,
            f"Demande rejetée. L'utilisateur {req.requested_by.username} a été notifié."
        )
        return redirect('resources:aidrequest_list')


def home(request):
    faqs = FAQ.objects.all()
    return render(request, 'home.html', {'faqs': faqs})


# ============================================================================
# EXPORT PDF
# ============================================================================

class ExportResourcesPDFView(LoginRequiredMixin, View):
    """
    Vue pour exporter les ressources en PDF.
    Génère un PDF professionnel avec toutes les ressources validées (ou toutes si admin).
    """
    
    def get(self, request):
        """Génère et retourne le PDF des ressources."""
        # Récupérer les ressources selon les mêmes règles que ResourceListView
        queryset = Resource.objects.select_related("category", "club", "submitted_by")
        
        # Filtrer par validation (même logique que ResourceListView)
        if not is_admin(request.user):
            queryset = queryset.filter(is_validated=True)
        
        # Appliquer les mêmes filtres que la liste si présents
        search_query = request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        
        category_filter = request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        club_filter = request.GET.get('club', '')
        if club_filter:
            queryset = queryset.filter(club_id=club_filter)
        
        resources = queryset.order_by('-date_submitted')
        
        # Créer le buffer pour le PDF
        buffer = BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Conteneur pour les éléments du PDF
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#7c3aed'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Style pour les sous-titres
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#5b21b6'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        # Style pour le texte normal
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.leading = 14
        
        # Style pour les métadonnées
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=10
        )
        
        # En-tête
        title = Paragraph("Ressources", title_style)
        elements.append(title)
        
        # Date d'export
        export_date = timezone.now().strftime("%d/%m/%Y à %H:%M")
        date_text = Paragraph(f"<i>Export généré le {export_date}</i>", meta_style)
        elements.append(date_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # Informations sur le nombre de ressources
        count_text = Paragraph(
            f"<b>Nombre total de ressources : {resources.count()}</b>",
            normal_style
        )
        elements.append(count_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Tableau récapitulatif (optionnel - peut être commenté si trop long)
        if resources.count() <= 50:  # Afficher le tableau seulement si moins de 50 ressources
            # En-tête du tableau
            table_data = [['Titre', 'Catégorie', 'Club', 'Auteur', 'Date']]
            
            # Données du tableau
            for resource in resources[:50]:  # Limiter à 50 pour éviter les PDF trop longs
                club_name = resource.club.name if resource.club else "N/A"
                author_name = resource.submitted_by.get_full_name() or resource.submitted_by.username
                date_str = resource.date_submitted.strftime("%d/%m/%Y")
                
                # Tronquer le titre si trop long
                title_short = resource.title[:40] + "..." if len(resource.title) > 40 else resource.title
                
                table_data.append([
                    title_short,
                    resource.category.name,
                    club_name,
                    author_name,
                    date_str
                ])
            
            # Créer le tableau
            table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.9*inch])
            table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                # Lignes alternées
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                # Bordures
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                # Alignement du texte
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Détails complets de chaque ressource
        subtitle = Paragraph("Détails des ressources", subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 0.1*inch))
        
        for idx, resource in enumerate(resources, 1):
            # Titre de la ressource
            resource_title = Paragraph(
                f"<b>{idx}. {resource.title}</b>",
                subtitle_style
            )
            elements.append(resource_title)
            
            # Informations dans un tableau stylisé
            info_data = [
                ['<b>Catégorie:</b>', resource.category.name],
                ['<b>Club:</b>', resource.club.name if resource.club else "Non spécifié"],
                ['<b>Auteur:</b>', resource.submitted_by.get_full_name() or resource.submitted_by.username],
                ['<b>Date de soumission:</b>', resource.date_submitted.strftime("%d/%m/%Y à %H:%M")],
                ['<b>Statut:</b>', "Validée" if resource.is_validated else "En attente de validation"],
            ]
            
            info_table = Table(info_data, colWidths=[1.5*inch, 4.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5b21b6')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(info_table)
            
            # Description
            elements.append(Spacer(1, 0.1*inch))
            desc_title = Paragraph("<b>Description:</b>", normal_style)
            elements.append(desc_title)
            
            # Nettoyer la description pour le PDF (supprimer HTML si présent)
            description = resource.description.replace('\n', '<br/>')
            desc_para = Paragraph(description, normal_style)
            elements.append(desc_para)
            
            # Séparateur entre les ressources
            if idx < resources.count():
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(
                    "<hr width='100%' color='#e2e8f0'/>",
                    normal_style
                ))
                elements.append(Spacer(1, 0.2*inch))
        
        # Construire le PDF
        doc.build(elements)
        
        # Récupérer le contenu du buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Créer la réponse HTTP
        date_str = timezone.now().strftime("%d_%m_%Y")
        filename = f'ressources_export_{date_str}.pdf'
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response


# Alias pour compatibilité avec function-based view
def export_resources_pdf(request):
    """Fonction wrapper pour l'export PDF des ressources."""
    view = ExportResourcesPDFView.as_view()
    return view(request)


class ExportAidsPDFView(LoginRequiredMixin, View):
    """
    Vue pour exporter les aides en PDF.
    Génère un PDF professionnel avec toutes les aides validées (ou toutes si admin).
    """
    
    def get(self, request):
        """Génère et retourne le PDF des aides."""
        # Récupérer les aides selon les mêmes règles que AidListView
        queryset = Aid.objects.select_related("category", "club", "submitted_by")
        
        # Filtrer par validation (même logique que AidListView)
        if not is_admin(request.user):
            queryset = queryset.filter(is_validated=True)
        
        # Appliquer les mêmes filtres que la liste si présents
        search_query = request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        
        category_filter = request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        club_filter = request.GET.get('club', '')
        if club_filter:
            queryset = queryset.filter(club_id=club_filter)
        
        aids = queryset.order_by('-date_submitted')
        
        # Créer le buffer pour le PDF
        buffer = BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Conteneur pour les éléments du PDF
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#7c3aed'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Style pour les sous-titres
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#5b21b6'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        # Style pour le texte normal
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.leading = 14
        
        # Style pour les métadonnées
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=10
        )
        
        # En-tête
        title = Paragraph("Aides", title_style)
        elements.append(title)
        
        # Date d'export
        export_date = timezone.now().strftime("%d/%m/%Y à %H:%M")
        date_text = Paragraph(f"<i>Export généré le {export_date}</i>", meta_style)
        elements.append(date_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # Informations sur le nombre d'aides
        count_text = Paragraph(
            f"<b>Nombre total d'aides : {aids.count()}</b>",
            normal_style
        )
        elements.append(count_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Tableau récapitulatif (optionnel - peut être commenté si trop long)
        if aids.count() <= 50:  # Afficher le tableau seulement si moins de 50 aides
            # En-tête du tableau
            table_data = [['Titre', 'Catégorie', 'Club', 'Auteur', 'Date']]
            
            # Données du tableau
            for aid in aids[:50]:  # Limiter à 50 pour éviter les PDF trop longs
                club_name = aid.club.name if aid.club else "N/A"
                author_name = aid.submitted_by.get_full_name() or aid.submitted_by.username
                date_str = aid.date_submitted.strftime("%d/%m/%Y")
                
                # Tronquer le titre si trop long
                title_short = aid.title[:40] + "..." if len(aid.title) > 40 else aid.title
                
                table_data.append([
                    title_short,
                    aid.category.name,
                    club_name,
                    author_name,
                    date_str
                ])
            
            # Créer le tableau
            table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.9*inch])
            table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                # Lignes alternées
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                # Bordures
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                # Alignement du texte
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Détails complets de chaque aide
        subtitle = Paragraph("Détails des aides", subtitle_style)
        elements.append(subtitle)
        elements.append(Spacer(1, 0.1*inch))
        
        for idx, aid in enumerate(aids, 1):
            # Titre de l'aide
            aid_title = Paragraph(
                f"<b>{idx}. {aid.title}</b>",
                subtitle_style
            )
            elements.append(aid_title)
            
            # Informations dans un tableau stylisé
            info_data = [
                ['<b>Catégorie:</b>', aid.category.name],
                ['<b>Club:</b>', aid.club.name if aid.club else "Non spécifié"],
                ['<b>Auteur:</b>', aid.submitted_by.get_full_name() or aid.submitted_by.username],
                ['<b>Date de soumission:</b>', aid.date_submitted.strftime("%d/%m/%Y à %H:%M")],
                ['<b>Statut:</b>', "Validée" if aid.is_validated else "En attente de validation"],
            ]
            
            info_table = Table(info_data, colWidths=[1.5*inch, 4.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5b21b6')),
                ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(info_table)
            
            # Description
            elements.append(Spacer(1, 0.1*inch))
            desc_title = Paragraph("<b>Description:</b>", normal_style)
            elements.append(desc_title)
            
            # Nettoyer la description pour le PDF (supprimer HTML si présent)
            description = aid.description.replace('\n', '<br/>')
            desc_para = Paragraph(description, normal_style)
            elements.append(desc_para)
            
            # Séparateur entre les aides
            if idx < aids.count():
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(
                    "<hr width='100%' color='#e2e8f0'/>",
                    normal_style
                ))
                elements.append(Spacer(1, 0.2*inch))
        
        # Construire le PDF
        doc.build(elements)
        
        # Récupérer le contenu du buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Créer la réponse HTTP
        date_str = timezone.now().strftime("%d_%m_%Y")
        filename = f'aides_export_{date_str}.pdf'
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response


# Alias pour compatibilité avec function-based view
def export_aids_pdf(request):
    """Fonction wrapper pour l'export PDF des aides."""
    view = ExportAidsPDFView.as_view()
    return view(request)


# ============================================================================
# FAVORIS
# ============================================================================

@login_required
def toggle_favorite_resource(request, pk):
    """
    Vue pour ajouter ou retirer une ressource des favoris.
    Si la ressource est déjà en favori, elle est retirée.
    Sinon, elle est ajoutée.
    Accepte GET et POST pour plus de flexibilité.
    """
    if request.method != 'POST':
        # Pour GET, rediriger vers la page de détail
        return redirect('resources:resource_detail', pk=pk)
    
    resource = get_object_or_404(Resource, pk=pk)
    user = request.user
    
    # Vérifier si le favori existe déjà
    favorite, created = Favorite.objects.get_or_create(
        user=user,
        resource=resource,
        defaults={'aid': None}
    )
    
    if not created:
        # Le favori existe déjà, on le supprime
        favorite.delete()
        messages.success(request, f"'{resource.title}' a été retiré de vos favoris.")
    else:
        # Le favori a été créé
        messages.success(request, f"'{resource.title}' a été ajouté à vos favoris.")
    
    # Rediriger vers la page de détail de la ressource
    return redirect('resources:resource_detail', pk=pk)


@login_required
def toggle_favorite_aid(request, pk):
    """
    Vue pour ajouter ou retirer une aide des favoris.
    Si l'aide est déjà en favori, elle est retirée.
    Sinon, elle est ajoutée.
    Accepte GET et POST pour plus de flexibilité.
    """
    if request.method != 'POST':
        # Pour GET, rediriger vers la page de détail
        return redirect('resources:aid_detail', pk=pk)
    
    aid = get_object_or_404(Aid, pk=pk)
    user = request.user
    
    # Vérifier si le favori existe déjà
    favorite, created = Favorite.objects.get_or_create(
        user=user,
        aid=aid,
        defaults={'resource': None}
    )
    
    if not created:
        # Le favori existe déjà, on le supprime
        favorite.delete()
        messages.success(request, f"'{aid.title}' a été retiré de vos favoris.")
    else:
        # Le favori a été créé
        messages.success(request, f"'{aid.title}' a été ajouté à vos favoris.")
    
    # Rediriger vers la page de détail de l'aide
    return redirect('resources:aid_detail', pk=pk)


class FavoriteListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher tous les favoris de l'utilisateur connecté.
    Permet de filtrer par type (ressources/aides) et de rechercher par titre.
    """
    model = Favorite
    template_name = "resources/favorites_list.html"
    context_object_name = "favorites"
    paginate_by = 12

    def get_queryset(self):
        """Récupère les favoris de l'utilisateur connecté."""
        queryset = Favorite.objects.filter(user=self.request.user).select_related(
            'resource', 'aid', 'resource__category', 'aid__category',
            'resource__club', 'aid__club'
        )
        
        # Filtre par type (ressources ou aides)
        favorite_type = self.request.GET.get('type', '')
        if favorite_type == 'resources':
            queryset = queryset.filter(resource__isnull=False)
        elif favorite_type == 'aids':
            queryset = queryset.filter(aid__isnull=False)
        
        # Recherche par titre
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                models.Q(resource__title__icontains=search_query) |
                models.Q(aid__title__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Ajoute les paramètres de recherche et de filtre au contexte."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_type'] = self.request.GET.get('type', '')
        return context


@staff_member_required  # Restreint l'accès aux utilisateurs staff/admin
def admin_dashboard(request):
    """
    Vue du tableau de bord administrateur.
    Calcule les statistiques des ressources, aides, demandes et clubs les plus actifs.
    """
    # Calculer les dates pour cette semaine et ce mois avec timezone
    now = timezone.now()
    today = now.date()
    
    # Lundi de cette semaine (weekday() retourne 0 pour lundi, 6 pour dimanche)
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week_datetime = timezone.make_aware(
        datetime.combine(start_of_week, datetime.min.time())
    )
    
    # Premier jour du mois
    start_of_month = today.replace(day=1)
    start_of_month_datetime = timezone.make_aware(
        datetime.combine(start_of_month, datetime.min.time())
    )

    # Statistiques pour les ressources (utiliser date_submitted au lieu de created_at)
    resources_this_week = Resource.objects.filter(
        date_submitted__gte=start_of_week_datetime
    ).count()
    resources_this_month = Resource.objects.filter(
        date_submitted__gte=start_of_month_datetime
    ).count()

    # Statistiques pour les aides (utiliser date_submitted au lieu de created_at)
    aids_this_week = Aid.objects.filter(
        date_submitted__gte=start_of_week_datetime
    ).count()
    aids_this_month = Aid.objects.filter(
        date_submitted__gte=start_of_month_datetime
    ).count()

    # Statistiques pour les demandes d'aide par statut
    aid_requests_pending = AidRequest.objects.filter(status=AidRequest.STATUS_PENDING).count()
    aid_requests_approved = AidRequest.objects.filter(status=AidRequest.STATUS_APPROVED).count()
    aid_requests_rejected = AidRequest.objects.filter(status=AidRequest.STATUS_REJECTED).count()

    # Top 5 des clubs les plus actifs (par nombre total de ressources + aides liées)
    top_clubs = (
        Club.objects.annotate(
            total_resources=Count("resources"),
            total_aids=Count("aids"),
            total_activities=Count("resources") + Count("aids")
        )
        .filter(total_activities__gt=0)
        .order_by("-total_activities")[:5]
    )

    # Préparer les données pour les graphiques : ressources et aides par mois (6 derniers mois)
    months_data = []
    resources_by_month = []
    aids_by_month = []
    
    # Calculer les 6 derniers mois en utilisant une approche simple
    current_year = today.year
    current_month = today.month
    
    for i in range(5, -1, -1):  # 6 derniers mois (5, 4, 3, 2, 1, 0)
        # Calculer le mois cible
        target_month = current_month - i
        target_year = current_year
        
        # Gérer le passage d'année
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        
        # Premier jour du mois
        month_start = datetime(target_year, target_month, 1).date()
        
        # Dernier jour du mois
        last_day = calendar.monthrange(target_year, target_month)[1]
        month_end = datetime(target_year, target_month, last_day).date()
        
        month_start_datetime = timezone.make_aware(
            datetime.combine(month_start, datetime.min.time())
        )
        month_end_datetime = timezone.make_aware(
            datetime.combine(month_end, datetime.max.time())
        )
        
        months_data.append(month_start.strftime("%b %Y"))
        resources_by_month.append(
            Resource.objects.filter(
                date_submitted__gte=month_start_datetime,
                date_submitted__lte=month_end_datetime
            ).count()
        )
        aids_by_month.append(
            Aid.objects.filter(
                date_submitted__gte=month_start_datetime,
                date_submitted__lte=month_end_datetime
            ).count()
        )

    # Préparer les données pour le template
    context = {
        "resources_this_week": resources_this_week,
        "resources_this_month": resources_this_month,
        "aids_this_week": aids_this_week,
        "aids_this_month": aids_this_month,
        "aid_requests_pending": aid_requests_pending,
        "aid_requests_approved": aid_requests_approved,
        "aid_requests_rejected": aid_requests_rejected,
        "top_clubs": top_clubs,
        "months_data": months_data,
        "resources_by_month": resources_by_month,
        "aids_by_month": aids_by_month,
    }

    return render(request, "resources/admin_dashboard.html", context)
