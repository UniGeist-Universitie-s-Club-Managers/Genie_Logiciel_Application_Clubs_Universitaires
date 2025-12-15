from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import User, Membership, Contribution, EventParticipation, UserBadge
from .forms import RegisterForm
from appEvenements.models import Evenement
from resources.models import Resource, Aid, FAQ

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
            return redirect("dashboard")
        else:
            messages.error(request, "Identifiants incorrects.")
    return render(request, "accounts/login.html")

# -------------------- LOGOUT --------------------
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Déconnecté.")
    return redirect("login")

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
            return redirect("login")
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
        return redirect("login")
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
@login_required
def chatbot_view(request):
    user = request.user
    answer = None
    if request.method == 'POST':
        question = request.POST.get('question', '').lower()
        if 'combien' in question or 'total' in question or 'nombre' in question:
            total_contrib = Contribution.objects.filter(user=user).count()
            total_events = EventParticipation.objects.filter(user=user).count()
            answer = f"Tu as {total_contrib} contribution(s) et {total_events} événement(s) inscrits."
        elif 'badges' in question or 'badge' in question or 'récompense' in question:
            badges = UserBadge.objects.filter(user=user)
            if badges.exists():
                answer = "Badges obtenus: " + ", ".join([ub.badge.name for ub in badges])
            else:
                answer = "Tu n'as pas encore de badge."
        elif 'clubs' in question or 'club' in question:
            clubs = Membership.objects.filter(user=user, active=True)
            if clubs.exists():
                answer = "Membre de : " + ", ".join([m.club.name for m in clubs])
            else:
                answer = "Tu n'es membre d'aucun club actif."
        else:
            answer = "Désolé, je n'ai pas compris. Essaie : 'Combien de contributions', 'Badges', 'Clubs'."

    return render(request, 'accounts/chatbot.html', {'answer': answer})

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
        return redirect("login")
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
    total_events = Evenement.objects.count()
    upcoming_events = Evenement.objects.filter(statut='planifie').count()
    active_events = Evenement.objects.filter(statut='en_cours').count()
    completed_events = Evenement.objects.filter(statut='termine').count()
    context = {
        'events': events,
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
    events = Evenement.objects.all().order_by('-date_debut')
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
    clubs = Club.objects.all()
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
