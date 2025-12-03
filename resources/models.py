from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Club(models.Model):
    """Modèle pour représenter un club universitaire."""
    name = models.CharField(max_length=200, unique=True, verbose_name="Nom du club")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    """Catégorie pour les ressources et aides."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Resource(models.Model):
    """Ressource partagée par un club."""
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    file = models.FileField(upload_to="resources/", verbose_name="Fichier")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="resources",
        verbose_name="Catégorie",
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources",
        verbose_name="Club",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_resources",
        verbose_name="Soumis par",
    )
    date_submitted = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")
    is_validated = models.BooleanField(default=False, verbose_name="Validée")

    class Meta:
        ordering = ["-date_submitted"]

    def __str__(self) -> str:
        return self.title


class Aid(models.Model):
    """Aide proposée par un club."""
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    file = models.FileField(upload_to="aids/", verbose_name="Fichier", blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="aids",
        verbose_name="Catégorie",
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="aids",
        verbose_name="Club",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_aids",
        verbose_name="Soumis par",
    )
    date_submitted = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")
    is_validated = models.BooleanField(default=False, verbose_name="Validée")

    class Meta:
        ordering = ["-date_submitted"]

    def __str__(self) -> str:
        return self.title


class AidRequest(models.Model):
    """Demande de ressource ou d'aide par un membre."""
    TYPE_RESOURCE = "resource"
    TYPE_AID = "aid"
    TYPE_CHOICES = [
        (TYPE_RESOURCE, "Ressource"),
        (TYPE_AID, "Aide"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_APPROVED, "Approuvée"),
        (STATUS_REJECTED, "Rejetée"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    description = models.TextField(verbose_name="Description")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name="Demandé par",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="Statut")
    date_requested = models.DateTimeField(auto_now_add=True, verbose_name="Date de demande")

    class Meta:
        ordering = ["-date_requested"]

    def __str__(self) -> str:
        return f"{self.get_type_display()} - {self.requested_by}"


class Guide(models.Model):
    """Modèle pour représenter un guide de démarrage."""
    title = models.CharField(max_length=255, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class FAQEntry(models.Model):
    """Modèle pour représenter une entrée de FAQ."""
    question = models.CharField(max_length=255, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question


class FichePDF(models.Model):
    """Modèle pour stocker les informations nécessaires à la génération de fiches PDF."""
    title = models.CharField(max_length=255, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return self.title


class FAQ(models.Model):
    """Modèle pour stocker les questions et réponses de la FAQ."""
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class Favorite(models.Model):
    """
    Modèle pour gérer les favoris des utilisateurs.
    Permet de sauvegarder des ressources ou des aides.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Utilisateur"
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        null=True,
        blank=True,
        verbose_name="Ressource"
    )
    aid = models.ForeignKey(
        Aid,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        null=True,
        blank=True,
        verbose_name="Aide"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        # Empêcher les doublons : un utilisateur ne peut pas avoir deux fois la même ressource/aide
        unique_together = [
            ('user', 'resource'),
            ('user', 'aid'),
        ]
        # Contrainte : au moins une des deux relations doit être définie
        constraints = [
            models.CheckConstraint(
                check=models.Q(resource__isnull=False) | models.Q(aid__isnull=False),
                name='favorite_must_have_resource_or_aid'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        if self.resource:
            return f"{self.user.username} - {self.resource.title}"
        elif self.aid:
            return f"{self.user.username} - {self.aid.title}"
        return f"{self.user.username} - Favori"

    def clean(self):
        """Validation : une favorite doit avoir soit une ressource, soit une aide, mais pas les deux."""
        from django.core.exceptions import ValidationError
        if not self.resource and not self.aid:
            raise ValidationError("Un favori doit être associé à une ressource ou une aide.")
        if self.resource and self.aid:
            raise ValidationError("Un favori ne peut pas être associé à la fois à une ressource et une aide.")

