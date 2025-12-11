from django import template

register = template.Library()


def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur."""
    return user.is_authenticated and user.is_staff


def is_organizer(user):
    """Vérifie si l'utilisateur est un organisateur."""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name="Organisateur").exists() or user.is_staff


@register.filter
def is_user_admin(user):
    """Vérifie si l'utilisateur est un administrateur."""
    return is_admin(user)


@register.filter
def is_user_organizer(user):
    """Vérifie si l'utilisateur est un organisateur."""
    return is_organizer(user)
