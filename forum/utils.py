from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Forum, Thread, Post, Survey


def get_forum_or_403(forum_pk, user):
    """Retourne un forum s'il est lisible par l'utilisateur, sinon 403."""
    forum = get_object_or_404(Forum, pk=forum_pk)
    if not forum.can_read(user):
        raise PermissionDenied("Accès refusé au forum privé.")
    return forum


def get_thread_or_403(thread_pk, user):
    """Retourne un thread accessible ou lève 403."""
    thread = get_object_or_404(Thread.objects.select_related('forum', 'forum__club'), pk=thread_pk)
    if not thread.can_view(user):
        raise PermissionDenied("Accès refusé à ce sujet.")
    return thread


def get_post_or_403(post_pk, user):
    """Retourne un post accessible ou lève 403."""
    post = get_object_or_404(Post.objects.select_related('thread', 'thread__forum', 'thread__forum__club'), pk=post_pk)
    if not post.can_view(user):
        raise PermissionDenied("Accès refusé à cette réponse.")
    return post


def get_survey_or_403(survey_pk, user):
    """Retourne un sondage accessible ou lève 403."""
    survey = get_object_or_404(Survey.objects.select_related('forum', 'forum__club'), pk=survey_pk)
    if not survey.can_view(user):
        raise PermissionDenied("Accès refusé à ce sondage.")
    return survey


def user_is_responsible_or_admin(user, club):
    """True si l'utilisateur est admin ou responsable du club donné."""
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or (club and club.responsible_id == user.id))
    )
