from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class Club(models.Model):
    """Modèle pour les clubs qui peuvent avoir des forums privés"""
    name = models.CharField(max_length=255, verbose_name="Nom du club")
    description = models.TextField(verbose_name="Description", blank=True)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_clubs',
        verbose_name="Responsable"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='clubs',
        blank=True,
        verbose_name="Membres"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Club"
        verbose_name_plural = "Clubs"


class Forum(models.Model):
    """Modèle pour les forums publics et privés (US 9.1 et 9.2)"""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Privé')
    ]
    
    title = models.CharField(max_length=255, verbose_name="Titre du forum")
    description = models.TextField(verbose_name="Description")
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='public',
        verbose_name="Visibilité"
    )
    club = models.OneToOneField(
        Club,
        on_delete=models.CASCADE,
        related_name='forum',
        null=True,
        blank=True,
        verbose_name="Club associé",
        help_text="Chaque club peut posséder au plus un forum privé."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_forums',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        # Un forum privé doit être associé à un club
        if self.visibility == 'private' and not self.club:
            raise ValidationError({
                'club': _("Un forum privé doit être associé à un club.")
            })
        
        # Si le forum est public, on s'assure qu'il n'est pas associé à un club
        if self.visibility == 'public' and self.club:
            self.club = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def is_private(self):
        """Vérifie si le forum est privé"""
        return self.visibility == 'private'

    def can_read(self, user):
        """True si l'utilisateur peut lire le forum."""
        if not self.is_private():
            return True
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if not self.club:
            return False
        if user == self.club.responsible:
            return True
        return self.club.members.filter(pk=user.pk).exists()

    def can_write(self, user):
        """True si l'utilisateur peut écrire dans le forum."""
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if not self.is_private():
            return True
        if not self.club:
            return False
        if user == self.club.responsible:
            return True
        return self.club.members.filter(pk=user.pk).exists()

    def can_manage(self, user):
        """Vérifie si un utilisateur peut gérer le forum"""
        if not user.is_authenticated:
            return False
            
        if user.is_superuser:
            return True
            
        if not self.is_private():
            return user == self.created_by
            
        if not self.club:
            return False
            
        return user == self.club.responsible

    def get_absolute_url(self):
        return reverse('forum:forum-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Forum"
        verbose_name_plural = "Forums"


class Thread(models.Model):
    """Modèle pour les threads/sujets de discussion (US 10.1)"""
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        related_name='threads',
        verbose_name="Forum"
    )
    title = models.CharField(max_length=255, verbose_name="Titre")
    body = models.TextField(verbose_name="Contenu")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='threads',
        verbose_name="Auteur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False, verbose_name="Épinglé")
    is_closed = models.BooleanField(default=False, verbose_name="Fermé")
    
    def clean(self):
        # Un thread doit toujours être associé à un forum
        if not self.forum_id:
            raise ValidationError({
                'forum': _("Un thread doit être associé à un forum.")
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def can_view(self, user):
        """Délègue au forum la vérification de lecture."""
        return self.forum.can_read(user)
        
    def can_edit(self, user):
        """Autorise l'auteur ou tout utilisateur ayant le droit d'écrire."""
        if not user or not user.is_authenticated:
            return False
        if user == self.author:
            return True
        return self.forum.can_write(user)
        
    def can_delete(self, user):
        """Autorise suppression si auteur ou permission d'écriture."""
        if not user or not user.is_authenticated:
            return False
        if user == self.author:
            return True
        return self.forum.can_write(user)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:thread-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Thread"
        verbose_name_plural = "Threads"


class Post(models.Model):
    """Modèle pour les posts/réponses (US 10.3 et 11.4)"""
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Thread"
    )
    content = models.TextField(verbose_name="Contenu")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Auteur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_modified = models.BooleanField(default=False, verbose_name="Modifié")
    
    def clean(self):
        # Un post doit toujours être associé à un thread
        if not self.thread_id:
            raise ValidationError({
                'thread': _("Un post doit être associé à un thread.")
            })
    
    def save(self, *args, **kwargs):
        # Marquer comme modifié si c'est une mise à jour
        if self.pk:
            self.is_modified = True
        self.full_clean()
        super().save(*args, **kwargs)
    
    def can_view(self, user):
        """Délègue au forum la vérification de lecture."""
        return self.thread.forum.can_read(user)
        
    def can_edit(self, user):
        """Autorise l'auteur ou tout utilisateur ayant le droit d'écrire."""
        if not user or not user.is_authenticated:
            return False
        if user == self.author:
            return True
        return self.thread.forum.can_write(user)
        
    def can_delete(self, user):
        """Autorise suppression si auteur ou permission d'écriture."""
        if not user or not user.is_authenticated:
            return False
        if user == self.author:
            return True
        return self.thread.forum.can_write(user)

    def __str__(self):
        return f"Réponse de {self.author} dans {self.thread.title}"

    class Meta:
        ordering = ['created_at']
        verbose_name = "Post"
        verbose_name_plural = "Posts"


class Survey(models.Model):
    """Modèle pour les sondages (US 10.2)"""
    forum = models.ForeignKey(
        Forum,
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name="Forum"
    )
    title = models.CharField(max_length=255, verbose_name="Titre du sondage")
    description = models.TextField(verbose_name="Description", blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name="Auteur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closes_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de clôture")
    is_closed = models.BooleanField(default=False, verbose_name="Sondage clôturé")
    
    def clean(self):
        # Un sondage doit toujours être associé à un forum
        if not self.forum_id:
            raise ValidationError({
                'forum': _("Un sondage doit être associé à un forum.")
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def can_view(self, user):
        """Délègue au forum la vérification de lecture."""
        return self.forum.can_read(user)
        
    def can_vote(self, user):
        """Vérifie si un utilisateur peut voter à ce sondage"""
        if not user or not user.is_authenticated:
            return False
            
        if self.is_closed or (self.closes_at and self.closes_at < timezone.now()):
            return False

        if not self.forum.can_read(user):
            return False

        if self.forum.is_private() and not self.forum.can_write(user):
            return False
                
        # Vérifier si l'utilisateur a déjà voté
        return not self.votes.filter(user=user).exists()
        
    def can_manage(self, user):
        """Vérifie si un utilisateur peut gérer ce sondage"""
        if not user or not user.is_authenticated:
            return False
        if user == self.author:
            return True
        return self.forum.can_write(user)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:survey-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Sondage"
        verbose_name_plural = "Sondages"


class SurveyOption(models.Model):
    """Options de réponse pour un sondage"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255, verbose_name="Texte de l'option")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text} ({self.survey.title})"

    class Meta:
        verbose_name = "Option de sondage"
        verbose_name_plural = "Options de sondage"


class SurveyVote(models.Model):
    """Vote d'un utilisateur sur un sondage"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(SurveyOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='survey_votes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} a voté pour {self.option.text}"

    class Meta:
        unique_together = ('survey', 'user')  # Un utilisateur ne peut voter qu'une fois par sondage
        verbose_name = "Vote"
        verbose_name_plural = "Votes"

