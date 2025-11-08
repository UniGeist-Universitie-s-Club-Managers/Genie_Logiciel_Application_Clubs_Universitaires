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