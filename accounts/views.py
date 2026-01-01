from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse
from .models import User, Membership, Contribution, EventParticipation, UserBadge
from .forms import RegisterForm
from appEvenements.models import Evenement
from resources.models import Resource, Aid, FAQ
from clubApp.models import Club
import requests
import json
import os
import sys
import google.genai as genai

# -------------------- LOGIN --------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Connexion réussie !")
            next_url = request.POST.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Identifiants incorrects.")
    return render(request, "accounts/login.html")

# -------------------- LOGOUT --------------------
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Déconnecté.")
    return redirect("accounts:login")

# -------------------- REGISTER --------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                is_active=True
            )
            # Champs optionnels
            user.phone = form.cleaned_data.get("phone")
            user.address = form.cleaned_data.get("address")
            user.save()
            messages.success(request, "Compte créé avec succès !")
            return redirect("accounts:login")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

# -------------------- PROFILE --------------------
@login_required
def profile_view(request):
    user = request.user
    memberships = Membership.objects.filter(user=user, active=True).select_related('club')
    contributions = Contribution.objects.filter(user=user).order_by('-created_at')[:5]
    participations = EventParticipation.objects.filter(user=user).select_related('event').order_by('-registered_at')[:5]
    badges = UserBadge.objects.filter(user=user).order_by('-awarded_at')[:5]

    context = {
        "user": user,
        "memberships": memberships,
        "contributions": contributions,
        "participations": participations,
        "badges": badges,
    }
    return render(request, "accounts/profile.html", context)

# -------------------- DELETE ACCOUNT --------------------
@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Compte supprimé.")
        return redirect("accounts:login")
    return render(request, "accounts/delete_confirm.html")

# -------------------- DASHBOARD --------------------
@login_required
def dashboard_view(request):
    user = request.user
    memberships = Membership.objects.filter(user=user, active=True).select_related('club')
    contributions = Contribution.objects.filter(user=user).order_by('-created_at')[:6]
    upcoming_events = EventParticipation.objects.filter(
        user=user, event__start__gte=timezone.now()
    ).select_related('event')[:5]
    badges = [ub.badge for ub in UserBadge.objects.filter(user=user)]

    total_contributions = Contribution.objects.filter(user=user).count()
    total_events = EventParticipation.objects.filter(user=user).count()

    context = {
        'user': user,
        'memberships': memberships,
        'contributions': contributions,
        'upcoming_events': upcoming_events,
        'badges': badges,
        'total_contributions': total_contributions,
        'total_events': total_events,
    }
    return render(request, 'accounts/dashboard.html', context)

# -------------------- HISTORY --------------------
@login_required
def history_view(request):
    user = request.user
    memberships = Membership.objects.filter(user=user).select_related('club').order_by('-joined_at')
    contributions = Contribution.objects.filter(user=user).order_by('-created_at')
    participations = EventParticipation.objects.filter(user=user).select_related('event').order_by('-registered_at')
    badges = UserBadge.objects.filter(user=user).order_by('-awarded_at')

    context = {
        'memberships': memberships,
        'contributions': contributions,
        'participations': participations,
        'badges': badges,
    }
    return render(request, 'accounts/history.html', context)

# -------------------- CHATBOT --------------------

def _configure_gemini():
    """Configure Gemini API with key from settings"""
    api_key = getattr(settings, 'GOOGLE_API_KEY', None)
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

@login_required
def chatbot_view(request):
    user = request.user
    answer = None

    # Get API key from Django settings (which loads from .env at startup)
    api_key = getattr(settings, 'GOOGLE_API_KEY', None)

    # Debug: Print API key status
    print(f"DEBUG: GOOGLE_API_KEY present: {bool(api_key)}")
    print(f"DEBUG: GOOGLE_API_KEY length: {len(api_key) if api_key else 0}")
    print(f"DEBUG: GOOGLE_API_KEY value: {api_key[:10] if api_key else 'None'}...")

    if not api_key:
        answer = "Erreur: Clé API Google Gemini non configurée. Vérifiez votre fichier .env"
        context = {'answer': answer, 'debug_api': {'present': False, 'length': 0}}
        return render(request, 'accounts/chatbot.html', context)
    
    # Configure Gemini
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        answer = f"Erreur lors de la configuration de Gemini: {str(e)}"
        context = {'answer': answer, 'debug_api': {'present': True, 'length': len(api_key) if api_key else 0}}
        return render(request, 'accounts/chatbot.html', context)
    
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()

        # Check if the question is about recommendations
        recommendation_keywords = ['recommend', 'suggest', 'clubs', 'resources', 'aides', 'events', 'événements', 'like', 'interested', 'what should i']
        is_recommendation = any(keyword in question.lower() for keyword in recommendation_keywords) or not question

        if is_recommendation:
            # Use recommendation logic
            memberships = Membership.objects.filter(user=user).select_related('club')
            contributions = Contribution.objects.filter(user=user).select_related('club')
            participations = EventParticipation.objects.filter(user=user).select_related('event__club')

            clubs_data = [
                {
                    "club_name": m.club.name,
                    "joined_date": m.joined_at.strftime('%Y-%m-%d'),
                    "role": m.role,
                    "active": m.active
                }
                for m in memberships
            ]
            contributions_data = [
                {
                    "title": c.title,
                    "club": c.club.name if c.club else "General",
                    "created_at": c.created_at.strftime('%Y-%m-%d'),
                    "score": c.score
                }
                for c in contributions
            ]
            events_data = [
                {
                    "event_title": p.event.title,
                    "club": p.event.club.name,
                    "registered_at": p.registered_at.strftime('%Y-%m-%d'),
                    "attended": p.attended
                }
                for p in participations
            ]
            user_data = {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "memberships": clubs_data,
                "contributions": contributions_data,
                "event_participations": events_data,
                "payments": []  # No Payment model, so empty
            }
            json_data = json.dumps(user_data)

            # Call Google Gemini for recommendations
            if question:
                prompt = f"Based on this user's history: {json_data}, and their question: '{question}', provide personalized recommendations for clubs, resources, or events they might be interested in. Respond in French."
            else:
                prompt = f"Based on this user's history: {json_data}, recommend 5 university clubs they might be interested in joining. Provide reasons for each recommendation based on their past memberships, contributions, and event participations. Respond in French."
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                answer = response.text
            except Exception as e:
                answer = f"Erreur API Gemini: {str(e)}"
        else:
            # General chatbot logic
            memberships = Membership.objects.filter(user=user, active=True).select_related('club')
            clubs_data = [
                {
                    "club_name": m.club.name,
                    "club_category": "General",
                    "joined_date": m.joined_at.strftime('%Y-%m-%d')
                }
                for m in memberships
            ]
            user_data = {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "clubs": clubs_data,
                "payments": []
            }
            json_data = json.dumps(user_data)

            prompt = f"User question: {question}\n\nUser data: {json_data}\n\nYou are a helpful assistant for a university club management system. Answer questions about clubs, events, resources, or provide general assistance. Respond in French."
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                answer = response.text
            except Exception as e:
                answer = f"Erreur API Gemini: {str(e)}"

    return render(request, 'accounts/chatbot.html', {'answer': answer, 'debug_api': {'present': True, 'length': len(api_key) if api_key else 0}})



# -------------------- VERIFY EMAIL --------------------
def verify_email(request, uidb64, token):
    UserModel = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre email a été vérifié avec succès !")
        return redirect("accounts:login")
    else:
        return render(request, "accounts/failed_verification.html")

# -------------------- ENVOI EMAIL DE TEST --------------------
@login_required
def send_test_email(request):
    send_mail(
        subject='Test UniGeist',
        message='Ceci est un mail de test envoyé depuis votre application Django.',
        from_email=None,  # utilisera DEFAULT_FROM_EMAIL
        recipient_list=['noobbuddha@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("Email envoyé ! Vérifie ta boîte Gmail.")

def fake_verify_success(request):
    return render(request, "accounts/verify_success.html")

# -------------------- HOME PAGES --------------------
def clubs_home_view(request):
    return render(request, 'clubs_home.html')

def events_home_view(request):
    events = Evenement.objects.filter(statut__in=['planifie', 'en_cours']).order_by('date_debut')[:6]
    featured_events = Evenement.objects.filter(featured=True).order_by('-date_debut')[:6]
    total_events = Evenement.objects.count()
    upcoming_events = Evenement.objects.filter(statut='planifie').count()
    active_events = Evenement.objects.filter(statut='en_cours').count()
    completed_events = Evenement.objects.filter(statut='termine').count()
    context = {
        'events': events,
        'featured_events': featured_events,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'active_events': active_events,
        'completed_events': completed_events,
    }
    return render(request, 'events_home.html', context)

def forums_home_view(request):
    from django.shortcuts import redirect
    return redirect('forum:thread-list')

def resources_home_view(request):
    recent_resources = Resource.objects.filter(is_validated=True).order_by('-date_submitted')[:6]
    total_resources = Resource.objects.filter(is_validated=True).count()
    total_aids = Aid.objects.filter(is_validated=True).count()
    context = {
        'recent_resources': recent_resources,
        'total_resources': total_resources,
        'total_aids': total_aids,
    }
    return render(request, 'resources_home.html', context)

def help_home_view(request):
    faqs = FAQ.objects.all()[:6]
    total_faqs = FAQ.objects.count()
    total_guides = 6  # Placeholder
    total_aids = Aid.objects.count()
    context = {
        'faqs': faqs,
        'total_faqs': total_faqs,
        'total_guides': total_guides,
        'total_aids': total_aids,
    }
    return render(request, 'help_home.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    """Interface admin personnalisée accessible uniquement aux admins"""
    context = {
        'title': 'Panneau d\'Administration',
        'entities': [
            {
                'name': 'Comptes',
                'url': 'admin_accounts',
                'description': 'Gérer les utilisateurs, badges, clubs, adhésions'
            },
            {
                'name': 'Événements',
                'url': 'admin_events',
                'description': 'Gérer les événements et participations'
            },
            {
                'name': 'Forums',
                'url': 'admin_forums',
                'description': 'Gérer les forums, sujets et sondages'
            },
            {
                'name': 'Ressources',
                'url': 'admin_resources',
                'description': 'Gérer les ressources éducatives'
            },
            {
                'name': 'Aides',
                'url': 'admin_aids',
                'description': 'Gérer les demandes d\'aide'
            },
            {
                'name': 'Clubs',
                'url': 'admin_clubs',
                'description': 'Gérer les clubs et leurs membres'
            },
            {
                'name': 'Sondages',
                'url': 'admin_surveys',
                'description': 'Gérer les sondages et options'
            },
            {
                'name': 'Sujets',
                'url': 'admin_threads',
                'description': 'Gérer les sujets de discussion'
            },
        ]
    }
    return render(request, 'admin_panel.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_accounts(request):
    """Interface admin pour les comptes"""
    users = User.objects.all().order_by('-date_joined')
    context = {
        'title': 'Administration des Comptes',
        'object_list': users,
        'entity_name': 'Comptes'
    }
    return render(request, 'admin_accounts.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_events(request):
    """Interface admin pour les événements"""
    from django.db.models import Count
    events = Evenement.objects.all().annotate(
        participant_count=Count('participants')
    ).order_by('-date_debut')
    context = {
        'title': 'Administration des Événements',
        'object_list': events,
        'entity_name': 'Événements'
    }
    return render(request, 'admin_events.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_forums(request):
    """Interface admin pour les forums"""
    from forums.forum.models import Forum
    forums = Forum.objects.all()
    context = {
        'title': 'Administration des Forums',
        'object_list': forums,
        'entity_name': 'Forums'
    }
    return render(request, 'admin_forums.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_resources(request):
    """Interface admin pour les ressources"""
    resources = Resource.objects.all().order_by('-date_submitted')
    context = {
        'title': 'Administration des Ressources',
        'object_list': resources,
        'entity_name': 'Ressources'
    }
    return render(request, 'admin_resources.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_aids(request):
    """Interface admin pour les aides"""
    aids = Aid.objects.all().order_by('-date_submitted')
    context = {
        'title': 'Administration des Aides',
        'object_list': aids,
        'entity_name': 'Aides'
    }
    return render(request, 'admin_aids.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_clubs(request):
    """Interface admin pour les clubs"""
    clubs = Club.objects.all().order_by('-established_date')
    context = {
        'title': 'Administration des Clubs',
        'object_list': clubs,
        'entity_name': 'Clubs'
    }
    return render(request, 'admin_clubs.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_surveys(request):
    """Interface admin pour les sondages"""
    from forums.forum.models import Survey
    surveys = Survey.objects.all().order_by('-created_at')
    context = {
        'title': 'Administration des Sondages',
        'object_list': surveys,
        'entity_name': 'Sondages'
    }
    return render(request, 'admin_surveys.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_threads(request):
    """Interface admin pour les sujets"""
    from forums.forum.models import Thread
    threads = Thread.objects.all().order_by('-created_at')
    context = {
        'title': 'Administration des Sujets',
        'object_list': threads,
        'entity_name': 'Sujets'
    }
    return render(request, 'admin_threads.html', context)

# -------------------- ADMIN EDIT/DELETE VIEWS --------------------

@user_passes_test(lambda u: u.is_superuser)
def admin_user_edit(request, pk):
    """Modifier un utilisateur"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        # Simple update - in production, use a proper form
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_superuser = request.POST.get('is_superuser') == 'on'
        user.save()
        messages.success(request, f'Utilisateur {user.username} modifié avec succès.')
        return redirect('admin_accounts')
    return render(request, 'admin_user_edit.html', {'user': user})

@user_passes_test(lambda u: u.is_superuser)
def admin_user_delete(request, pk):
    """Supprimer un utilisateur"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Utilisateur {username} supprimé avec succès.')
        return redirect('admin_accounts')
    return render(request, 'admin_user_delete.html', {'user': user})

@user_passes_test(lambda u: u.is_superuser)
def admin_event_edit(request, pk):
    """Modifier un événement"""
    event = get_object_or_404(Evenement, pk=pk)
    if request.method == 'POST':
        # Simple update - in production, use a proper form
        event.titre = request.POST.get('titre', event.titre)
        event.description = request.POST.get('description', event.description)
        event.save()
        messages.success(request, f'Événement {event.titre} modifié avec succès.')
        return redirect('admin_events')
    return render(request, 'admin_event_edit.html', {'event': event})

@user_passes_test(lambda u: u.is_superuser)
def admin_event_delete(request, pk):
    """Supprimer un événement"""
    event = get_object_or_404(Evenement, pk=pk)
    if request.method == 'POST':
        titre = event.titre
        event.delete()
        messages.success(request, f'Événement {titre} supprimé avec succès.')
        return redirect('admin_events')
    return render(request, 'admin_event_delete.html', {'event': event})

@user_passes_test(lambda u: u.is_superuser)
def admin_forum_edit(request, pk):
    """Modifier un forum"""
    from forums.forum.models import Forum
    forum = get_object_or_404(Forum, pk=pk)
    if request.method == 'POST':
        forum.name = request.POST.get('name', forum.name)
        forum.description = request.POST.get('description', forum.description)
        forum.save()
        messages.success(request, f'Forum {forum.name} modifié avec succès.')
        return redirect('admin_forums')
    return render(request, 'admin_forum_edit.html', {'forum': forum})

@user_passes_test(lambda u: u.is_superuser)
def admin_forum_delete(request, pk):
    """Supprimer un forum"""
    from forums.forum.models import Forum
    forum = get_object_or_404(Forum, pk=pk)
    if request.method == 'POST':
        name = forum.name
        forum.delete()
        messages.success(request, f'Forum {name} supprimé avec succès.')
        return redirect('admin_forums')
    return render(request, 'admin_forum_delete.html', {'forum': forum})

@user_passes_test(lambda u: u.is_superuser)
def admin_resource_edit(request, pk):
    """Modifier une ressource"""
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.title = request.POST.get('title', resource.title)
        resource.description = request.POST.get('description', resource.description)
        resource.is_validated = request.POST.get('is_validated') == 'on'
        resource.save()
        messages.success(request, f'Ressource {resource.title} modifiée avec succès.')
        return redirect('admin_resources')
    return render(request, 'admin_resource_edit.html', {'resource': resource})

@user_passes_test(lambda u: u.is_superuser)
def admin_resource_delete(request, pk):
    """Supprimer une ressource"""
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        title = resource.title
        resource.delete()
        messages.success(request, f'Ressource {title} supprimée avec succès.')
        return redirect('admin_resources')
    return render(request, 'admin_resource_delete.html', {'resource': resource})

@user_passes_test(lambda u: u.is_superuser)
def admin_aid_edit(request, pk):
    """Modifier une aide"""
    aid = get_object_or_404(Aid, pk=pk)
    if request.method == 'POST':
        aid.title = request.POST.get('title', aid.title)
        aid.description = request.POST.get('description', aid.description)
        aid.is_validated = request.POST.get('is_validated') == 'on'
        aid.save()
        messages.success(request, f'Aide {aid.title} modifiée avec succès.')
        return redirect('admin_aids')
    return render(request, 'admin_aid_edit.html', {'aid': aid})

@user_passes_test(lambda u: u.is_superuser)
def admin_aid_delete(request, pk):
    """Supprimer une aide"""
    aid = get_object_or_404(Aid, pk=pk)
    if request.method == 'POST':
        title = aid.title
        aid.delete()
        messages.success(request, f'Aide {title} supprimée avec succès.')
        return redirect('admin_aids')
    return render(request, 'admin_aid_delete.html', {'aid': aid})

@user_passes_test(lambda u: u.is_superuser)
def admin_club_edit(request, pk):
    """Modifier un club"""
    club = get_object_or_404(Club, pk=pk)
    if request.method == 'POST':
        club.name = request.POST.get('name', club.name)
        club.description = request.POST.get('description', club.description)
        club.save()
        messages.success(request, f'Club {club.name} modifié avec succès.')
        return redirect('admin_clubs')
    return render(request, 'admin_club_edit.html', {'club': club})

@user_passes_test(lambda u: u.is_superuser)
def admin_club_delete(request, pk):
    """Supprimer un club"""
    club = get_object_or_404(Club, pk=pk)
    if request.method == 'POST':
        name = club.name
        club.delete()
        messages.success(request, f'Club {name} supprimé avec succès.')
        return redirect('admin_clubs')
    return render(request, 'admin_club_delete.html', {'club': club})

@user_passes_test(lambda u: u.is_superuser)
def admin_survey_edit(request, pk):
    """Modifier un sondage"""
    from forums.forum.models import Survey
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == 'POST':
        survey.question = request.POST.get('question', survey.question)
        survey.save()
        messages.success(request, f'Sondage modifié avec succès.')
        return redirect('admin_surveys')
    return render(request, 'admin_survey_edit.html', {'survey': survey})

@user_passes_test(lambda u: u.is_superuser)
def admin_survey_delete(request, pk):
    """Supprimer un sondage"""
    from forums.forum.models import Survey
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == 'POST':
        survey.delete()
        messages.success(request, f'Sondage supprimé avec succès.')
        return redirect('admin_surveys')
    return render(request, 'admin_survey_delete.html', {'survey': survey})

@user_passes_test(lambda u: u.is_superuser)
def admin_thread_edit(request, pk):
    """Modifier un sujet"""
    from forums.forum.models import Thread
    thread = get_object_or_404(Thread, pk=pk)
    if request.method == 'POST':
        thread.title = request.POST.get('title', thread.title)
        thread.save()
        messages.success(request, f'Sujet {thread.title} modifié avec succès.')
        return redirect('admin_threads')
    return render(request, 'admin_thread_edit.html', {'thread': thread})

@user_passes_test(lambda u: u.is_superuser)
def admin_thread_delete(request, pk):
    """Supprimer un sujet"""
    from forums.forum.models import Thread
    thread = get_object_or_404(Thread, pk=pk)
    if request.method == 'POST':
        title = thread.title
        thread.delete()
        messages.success(request, f'Sujet {title} supprimé avec succès.')
        return redirect('admin_threads')
    return render(request, 'admin_thread_delete.html', {'thread': thread})

from django.http import JsonResponse

@user_passes_test(lambda u: u.is_superuser)
def admin_event_participants(request, event_id):
    """API pour récupérer la liste des participants d'un événement"""
    from appEvenements.models import Evenement, Participation
    try:
        event = Evenement.objects.get(id=event_id)
        participations = Participation.objects.filter(evenement=event).select_related('user').order_by('registered_at')
        participants = []
        for participation in participations:
            participants.append({
                'username': participation.user.username,
                'first_name': participation.user.first_name,
                'last_name': participation.user.last_name,
                'registered_at': participation.registered_at.strftime('%d/%m/%Y %H:%M'),
                'status': participation.get_status_display()
            })
        return JsonResponse({'participants': participants})
    except Evenement.DoesNotExist:
        return JsonResponse({'error': 'Événement non trouvé'}, status=404)
