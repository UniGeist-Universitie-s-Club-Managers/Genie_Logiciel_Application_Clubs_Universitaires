from django.db import models
from django.utils import timezone
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator

class Evenement(models.Model):
    id=models.AutoField(primary_key=True)
    titre = models.CharField(max_length=200, validators=[MinLengthValidator(6,"Le titre doit avoir au moins 6 caractères"), MaxLengthValidator(200), RegexValidator(r'^[a-zA-Z0-9\s.,!?-]+$', message="Le titre ne peut contenir que des lettres, chiffres, espaces et ponctuation basique.")])
    description = models.TextField( max_length=1000, validators=[validators.MinLengthValidator(10), validators.MaxLengthValidator(1000), validators.RegexValidator(r'^[a-zA-Z0-9\s.,!?-]+$', message="La description ne peut contenir que des lettres, chiffres, espaces et ponctuation basique.")])
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    lieu = models.CharField(max_length=200, validators=[validators.MinLengthValidator(5), validators.MaxLengthValidator(200), validators.RegexValidator(r'^[a-zA-Z0-9\s.,!?-]+$', message="Le lieu ne peut contenir que des lettres, chiffres, espaces et ponctuation basique.")])
    statut = models.CharField(max_length=50, choices=[('planifie', 'Planifié'), ('en_cours', 'En cours'), ('termine', 'Terminé'), ('annule', 'Annulé')])
    visibilite = models.CharField(max_length=50, choices=[('public', 'Public'), ('prive', 'Privé')])
    featured = models.BooleanField(default=False, help_text="Événement à la une")
    promotion_image = models.ImageField(upload_to='promotions/', blank=True, null=True, help_text="Image de promotion")
    promotion_description = models.TextField(blank=True, null=True, help_text="Description de promotion")

    def __str__(self):
        return self.titre
    def get_duree(self):
        return self.date_fin - self.date_debut
    def is_past(self):
        from django.utils import timezone
        return self.date_fin < timezone.now()
    def is_upcoming(self):
        from django.utils import timezone
        return self.date_debut > timezone.now()
    def is_ongoing(self):
        from django.utils import timezone
        now = timezone.now()
        return self.date_debut <= now <= self.date_fin
    def set_visibilite(self, nouvelle_visibilite):
        self.visibilite = nouvelle_visibilite
        self.save()
    
    def validate_dates(self):
        if self.date_fin <= self.date_debut:
            raise ValueError("La date de fin doit être postérieure à la date de début.")
    def save(self, *args, **kwargs):
        self.validate_dates()
        super().save(*args, **kwargs)