from django import forms
from .models import Club

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'established_date']
        widgets = {
            'established_date': forms.DateInput(attrs={'type': 'date'}), 
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40,
                                                 'placeholder': 'Enter club description here...'}),
        }