from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone

from .models import Forum, Thread, Post, Survey, Club

def get_forum_or_404(forum_pk, user):
    """
    Récupère un forum ou renvoie une 404.
    Vérifie également les permissions de lecture.
    """
    forum = get_object_or_404(Forum, pk=forum_pk)
    
    if not user.is_authenticated:
        if forum.visibility != 'public':
            raise PermissionDenied(_("Vous devez être connecté pour accéder à ce forum."))
        return forum
    
    if not forum.can_read(user):
        raise PermissionDenied(_("Vous n'avez pas la permission d'accéder à ce forum."))
    
    return forum

def get_thread_or_404(thread_pk, user, forum=None):
    """
    Récupère un thread ou renvoie une 404.
    Vérifie également les permissions de lecture.
    """
    thread = get_object_or_404(Thread.objects.select_related('forum', 'author'), pk=thread_pk)
    
    # Si un forum est spécifié, on vérifie que le thread lui appartient
    if forum and thread.forum != forum:
        raise PermissionDenied(_("Ce sujet n'appartient pas à ce forum."))
    
    # Vérification des permissions
    if not thread.can_view(user):
        raise PermissionDenied(_("Vous n'avez pas la permission de voir ce sujet."))
    
    return thread

def get_post_or_404(post_pk, user, thread=None):
    """
    Récupère un post ou renvoie une 404.
    Vérifie également les permissions de lecture.
    """
    post = get_object_or_404(
        Post.objects.select_related('thread__forum', 'author'),
        pk=post_pk
    )
    
    # Si un thread est spécifié, on vérifie que le post lui appartient
    if thread and post.thread != thread:
        raise PermissionDenied(_("Ce message n'appartient pas à ce sujet."))
    
    # Vérification des permissions
    if not post.can_view(user):
        raise PermissionDenied(_("Vous n'avez pas la permission de voir ce message."))
    
    return post

def get_survey_or_404(survey_pk, user, forum=None):
    """
    Récupère un sondage ou renvoie une 404.
    Vérifie également les permissions de lecture.
    """
    survey = get_object_or_404(
        Survey.objects.select_related('forum', 'author'),
        pk=survey_pk
    )
    
    # Si un forum est spécifié, on vérifie que le sondage lui appartient
    if forum and survey.forum != forum:
        raise PermissionDenied(_("Ce sondage n'appartient pas à ce forum."))
    
    # Vérification des permissions
    if not survey.can_view(user):
        raise PermissionDenied(_("Vous n'avez pas la permission de voir ce sondage."))
    
    return survey

class UserCanReadForumMixin:
    """Mixin pour vérifier qu'un utilisateur peut lire un forum"""
    def dispatch(self, request, *args, **kwargs):
        self.forum = get_forum_or_404(kwargs.get('pk'), request.user)
        return super().dispatch(request, *args, **kwargs)

class UserCanWriteForumMixin(UserCanReadForumMixin):
    """Mixin pour vérifier qu'un utilisateur peut écrire dans un forum"""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        if not request.user.is_authenticated:
            messages.error(request, _("Vous devez être connecté pour effectuer cette action."))
            return redirect('account_login')  # Assurez-vous d'avoir une vue de connexion configurée
            
        if not self.forum.can_write(request.user):
            messages.error(request, _("Vous n'avez pas la permission de publier dans ce forum."))
            return redirect('forum:forum-detail', pk=self.forum.pk)
            
        return response

class UserCanManageForumMixin(UserCanReadForumMixin):
    """Mixin pour vérifier qu'un utilisateur peut gérer un forum"""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        if not request.user.is_authenticated:
            messages.error(request, _("Vous devez être connecté pour effectuer cette action."))
            return redirect('account_login')
            
        if not self.forum.can_manage(request.user):
            messages.error(request, _("Vous n'avez pas la permission de gérer ce forum."))
            return redirect('forum:forum-detail', pk=self.forum.pk)
            
        return response

class UserCanEditThreadMixin(UserPassesTestMixin):
    """Mixin pour vérifier qu'un utilisateur peut modifier un thread"""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        thread = get_thread_or_404(self.kwargs.get('pk'), self.request.user)
        return thread.can_edit(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, _("Vous n'avez pas la permission de modifier ce sujet."))
        return redirect('forum:thread-detail', pk=self.kwargs.get('pk'))

class UserCanDeleteThreadMixin(UserPassesTestMixin):
    """Mixin pour vérifier qu'un utilisateur peut supprimer un thread"""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        thread = get_thread_or_404(self.kwargs.get('pk'), self.request.user)
        return thread.can_delete(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, _("Vous n'avez pas la permission de supprimer ce sujet."))
        return redirect('forum:thread-detail', pk=self.kwargs.get('pk'))

class UserCanEditPostMixin(UserPassesTestMixin):
    """Mixin pour vérifier qu'un utilisateur peut modifier un post"""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        post = get_post_or_404(self.kwargs.get('pk'), self.request.user)
        return post.can_edit(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, _("Vous n'avez pas la permission de modifier ce message."))
        return redirect('forum:thread-detail', pk=self.kwargs.get('thread_pk'))

class UserCanDeletePostMixin(UserPassesTestMixin):
    """Mixin pour vérifier qu'un utilisateur peut supprimer un post"""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        post = get_post_or_404(self.kwargs.get('pk'), self.request.user)
        return post.can_delete(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, _("Vous n'avez pas la permission de supprimer ce message."))
        return redirect('forum:thread-detail', pk=self.kwargs.get('thread_pk'))

class UserCanManageSurveyMixin(UserPassesTestMixin):
    """Mixin pour vérifier qu'un utilisateur peut gérer un sondage"""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        survey = get_survey_or_404(self.kwargs.get('pk'), self.request.user)
        return survey.can_manage(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, _("Vous n'avez pas la permission de gérer ce sondage."))
        return redirect('forum:survey-detail', pk=self.kwargs.get('pk'))

def check_forum_permission(user, forum, permission_type='read'):
    """
    Vérifie si un utilisateur a une certaine permission sur un forum
    
    Args:
        user: L'utilisateur à vérifier
        forum: Le forum sur lequel vérifier la permission
        permission_type: Le type de permission à vérifier ('read', 'write', 'manage')
    
    Returns:
        bool: True si l'utilisateur a la permission, False sinon
    """
    if not user.is_authenticated:
        return permission_type == 'read' and forum.visibility == 'public'
        
    if permission_type == 'read':
        return forum.can_read(user)
    elif permission_type == 'write':
        return forum.can_write(user)
    elif permission_type == 'manage':
        return forum.can_manage(user)
    return False

def check_thread_permission(user, thread, permission_type='view'):
    """
    Vérifie si un utilisateur a une certaine permission sur un thread
    
    Args:
        user: L'utilisateur à vérifier
        thread: Le thread sur lequel vérifier la permission
        permission_type: Le type de permission à vérifier ('view', 'edit', 'delete')
    
    Returns:
        bool: True si l'utilisateur a la permission, False sinon
    """
    if not user.is_authenticated:
        return permission_type == 'view' and thread.forum.visibility == 'public'
        
    if permission_type == 'view':
        return thread.can_view(user)
    elif permission_type == 'edit':
        return thread.can_edit(user)
    elif permission_type == 'delete':
        return thread.can_delete(user)
    return False

def check_post_permission(user, post, permission_type='view'):
    """
    Vérifie si un utilisateur a une certaine permission sur un post
    
    Args:
        user: L'utilisateur à vérifier
        post: Le post sur lequel vérifier la permission
        permission_type: Le type de permission à vérifier ('view', 'edit', 'delete')
    
    Returns:
        bool: True si l'utilisateur a la permission, False sinon
    """
    if not user.is_authenticated:
        return permission_type == 'view' and post.thread.forum.visibility == 'public'
        
    if permission_type == 'view':
        return post.can_view(user)
    elif permission_type == 'edit':
        return post.can_edit(user)
    elif permission_type == 'delete':
        return post.can_delete(user)
    return False

def check_survey_permission(user, survey, permission_type='view'):
    """
    Vérifie si un utilisateur a une certaine permission sur un sondage
    
    Args:
        user: L'utilisateur à vérifier
        survey: Le sondage sur lequel vérifier la permission
        permission_type: Le type de permission à vérifier ('view', 'vote', 'manage')
    
    Returns:
        bool: True si l'utilisateur a la permission, False sinon
    """
    if not user.is_authenticated:
        return permission_type == 'view' and survey.forum.visibility == 'public'
        
    if permission_type == 'view':
        return survey.can_view(user)
    elif permission_type == 'vote':
        return survey.can_vote(user)
    elif permission_type == 'manage':
        return survey.can_manage(user)
    return False