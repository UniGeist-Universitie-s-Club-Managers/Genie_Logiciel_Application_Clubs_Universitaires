from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError  
# Create your models here.
class Club(models.Model):
    validatorTitle = RegexValidator(
        regex=r'^[A-Za-z0-9\s]+$',
        message="This field should contain only alphanumeric characters and spaces."
    )
    club_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, validators=[validatorTitle])
    description = models.TextField(validators=[MinLengthValidator(10,"Description must be at least 10 characters long.")], blank=True, null=True)
    established_date = models.DateField()
    
    def __str__(self):
        return self.name
    # def clean(self):
    #     if self.established_date > timezone.now():
    #         raise ValidationError("Established date cannot be in the future.")

    
class Demande_creation_club(models.Model):
        validatorTitle = RegexValidator(
        regex=r'^[A-Za-z0-9\s]+$',
        message="This field should contain only alphanumeric characters and spaces."
    )
        validatorName = RegexValidator(
        regex=r'^[A-Za-z\s]+$',
        message="This field should contain only alphabetic characters and spaces."
    )
        demande_id = models.AutoField(primary_key=True)
        club_name = models.CharField(max_length=100, validators=[validatorTitle])
        club_description = models.TextField(validators=[MinLengthValidator(10,"Description must be at least 10 characters long.")], blank=True, null=True)
        president_name = models.CharField(max_length=100, validators=[validatorName])
        vice_president_name = models.CharField(max_length=100, validators=[validatorName])
        requested_by = models.CharField(max_length=100, validators=[validatorName])
        emailResponsable = models.EmailField(max_length=254, blank=True, null=True)
        emailClub = models.EmailField(max_length=254, blank=True, null=True)
        tel = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?\d{8}$', message="Phone number must be entered in the format: '99999999'. Up to 8 digits allowed.")])
                
        def __str__(self):
            return f"Demande by {self.requested_by} for {self.club_name}"
        
        
    
        
        
        
        
        
        