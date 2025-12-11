from django import forms

from .models import Aid, AidRequest, Category, Club, Resource


class BaseBootstrapModelForm(forms.ModelForm):
    """Classe de base pour appliquer Bootstrap aux formulaires."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput) or isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "form-control")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault("class", "form-control")
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")


class ResourceForm(BaseBootstrapModelForm):
    class Meta:
        model = Resource
        fields = ["title", "description", "file", "category", "club"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class AidForm(BaseBootstrapModelForm):
    class Meta:
        model = Aid
        fields = ["title", "description", "file", "category", "club"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class AidRequestForm(BaseBootstrapModelForm):
    class Meta:
        model = AidRequest
        fields = ["type", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Décrivez la ressource ou l'aide que vous souhaitez..."}),
        }
