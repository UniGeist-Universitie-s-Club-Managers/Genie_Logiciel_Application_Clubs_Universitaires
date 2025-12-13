from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .models import User, Membership, Contribution, EventParticipation, UserBadge
from .forms import RegisterForm
from .utils import send_verification_email

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
                is_active=False
            )
            # Champs optionnels
            user.phone = form.cleaned_data.get("phone")
            user.address = form.cleaned_data.get("address")
            user.save()
            send_verification_email(request, user)
            messages.success(request, "Compte créé. Un email de vérification a été envoyé.")
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
