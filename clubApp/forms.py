from django import forms
from .models import Club, Demande_creation_club

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'established_date']
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date'}), 
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40,
                                                 'placeholder': 'Enter club description here...'}),
        }
    
class DemandeCreationClubForm(forms.ModelForm):
    class Meta:
        model = Demande_creation_club
        fields = ['club_name', 'club_description', 'president_name', 'vice_president_name', 'requested_by', 'emailResponsable','emailClub','tel']
        widgets = {
            'club_description': forms.Textarea(attrs={'rows': 4, 'cols': 40,
                                                      'placeholder': 'Enter club description here...'}),
        }