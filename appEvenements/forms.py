from django import forms
from .models import Evenement

class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = '__all__'
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'lieu': forms.TextInput(attrs={'placeholder': 'Lieu de l\'événement'}),
            'statut': forms.Select(),
            'visibilite': forms.Select(),
        }
        labels = {
            'titre': 'Titre de l\'événement',
            'description': 'Description',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'lieu': 'Lieu',
            'statut': 'Statut',
            'visibilite': 'Visibilité',
        }
        help_texts = {
            'titre': 'Entrez un titre clair et concis pour l\'événement.',
            'description': 'Fournissez une description détaillée de l\'événement.',
            'date_debut': 'Sélectionnez la date et l\'heure de début de l\'événement.',
            'date_fin': 'Sélectionnez la date et l\'heure de fin de l\'événement.',
            'lieu': 'Indiquez le lieu où se déroulera l\'événement.',
            'statut': 'Choisissez le statut actuel de l\'événement.',
            'visibilite': 'Définissez si l\'événement est public ou privé.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['visibilite'].initial = 'public'
        self.fields['statut'].initial = 'planifie'


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['promotion_description', 'promotion_image', 'featured']
        widgets = {
            'promotion_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description de promotion pour Facebook'}),
            'promotion_image': forms.FileInput(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'promotion_description': 'Description de promotion',
            'promotion_image': 'Image de promotion',
            'featured': 'Événement à la une',
        }
        help_texts = {
            'promotion_description': 'Entrez une description attrayante pour la promotion sur Facebook.',
            'promotion_image': 'Téléchargez une image pour accompagner la promotion.',
            'featured': 'Cochez pour mettre cet événement à la une sur la page d\'accueil.',
        }
            


