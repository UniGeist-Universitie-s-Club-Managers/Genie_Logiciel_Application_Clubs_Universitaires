from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur."""
    return user.is_authenticated and user.is_staff


def is_organizer(user):
    """Vérifie si l'utilisateur est un organisateur."""
    if not user.is_authenticated:
        return False
    # Vérifier si l'utilisateur est dans le groupe "Organisateur"
    return user.groups.filter(name="Organisateur").exists() or user.is_staff


def is_member(user):
    """Vérifie si l'utilisateur est un membre (tout utilisateur connecté)."""
    return user.is_authenticated


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin pour restreindre l'accès aux administrateurs uniquement."""
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def handle_no_permission(self):
        raise PermissionDenied("Vous devez être administrateur pour accéder à cette page.")


class OrganizerRequiredMixin(UserPassesTestMixin):
    """Mixin pour restreindre l'accès aux organisateurs et administrateurs."""
    
    def test_func(self):
        return is_organizer(self.request.user)
    
    def handle_no_permission(self):
        raise PermissionDenied("Vous devez être organisateur pour accéder à cette page.")


class MemberRequiredMixin(UserPassesTestMixin):
    """Mixin pour restreindre l'accès aux utilisateurs connectés."""
    
    def test_func(self):
        return is_member(self.request.user)
    
    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(self.request.get_full_path())


