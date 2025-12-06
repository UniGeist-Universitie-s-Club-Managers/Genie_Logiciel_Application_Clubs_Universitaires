# forum/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Post, Thread, Forum, Survey, SurveyOption, Club

User = get_user_model()


class ForumForm(forms.ModelForm):
    """Formulaire pour créer/modifier un forum (US 9.1 et 9.2)"""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and not self.user.is_superuser:
            self.fields['club'].queryset = Club.objects.filter(
                Q(responsible=self.user) | Q(members=self.user)
            ).distinct()

        if self.instance and self.instance.pk and self.instance.visibility == 'private':
            self.fields['club'].disabled = True
            self.fields['visibility'].disabled = True

    class Meta:
        model = Forum
        fields = ['title', 'description', 'visibility', 'club']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du forum'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description du forum'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'club': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Titre du forum',
            'description': 'Description',
            'visibility': 'Visibilité',
            'club': 'Club associé',
        }

    def clean(self):
        cleaned_data = super().clean()
        visibility = cleaned_data.get('visibility')
        club = cleaned_data.get('club')

        if visibility == 'private' and not club:
            self.add_error('club', _('Un forum privé doit être associé à un club.'))

        if visibility == 'private' and club and self.user:
            if not (self.user.is_superuser or self.user == club.responsible):
                raise ValidationError(
                    _("Vous n'avez pas la permission de créer un forum privé pour ce club."),
                    code='forbidden'
                )

        return cleaned_data


class VoteForm(forms.Form):
    """Formulaire pour voter à un sondage (US 10.2)"""
    option = forms.ModelChoiceField(
        queryset=SurveyOption.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Votre choix',
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop('survey', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.survey:
            self.fields['option'].queryset = self.survey.options.all()

    def clean(self):
        cleaned_data = super().clean()

        if self.survey and self.user:
            if not self.survey.can_vote(self.user):
                raise ValidationError(
                    _("Vous ne pouvez pas voter à ce sondage."),
                    code='voting_not_allowed'
                )

        return cleaned_data


class ThreadForm(forms.ModelForm):
    """Formulaire pour créer/modifier un thread (US 10.1)"""

    def __init__(self, *args, **kwargs):
        self.forum = kwargs.pop('forum', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        forums_qs = Forum.objects.all().select_related('club')
        if self.user and not self.user.is_superuser:
            access_q = Q(visibility='public') | Q(club__responsible=self.user) | Q(club__members=self.user)
            forums_qs = forums_qs.filter(access_q)

        if self.forum:
            self.fields['forum'].queryset = Forum.objects.filter(pk=self.forum.pk)
            self.fields['forum'].initial = self.forum
            self.fields['forum'].disabled = True
        else:
            self.fields['forum'].queryset = forums_qs.distinct()

    class Meta:
        model = Thread
        fields = ['forum', 'title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du sujet'}),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Contenu du sujet',
                'data-controller': 'markdown-editor'
            }),
        }
        labels = {
            'forum': 'Forum',
            'title': 'Titre',
            'body': 'Message',
        }

    def clean(self):
        cleaned_data = super().clean()
        forum = self.forum or cleaned_data.get('forum')

        if not forum:
            raise ValidationError(
                _("Un forum est requis pour créer un sujet."),
                code='missing_forum'
            )

        if self.user and not forum.can_write(self.user):
            raise ValidationError(
                _("Vous n'avez pas la permission de créer un sujet dans ce forum."),
                code='permission_denied'
            )

        self.forum = forum
        return cleaned_data

    def save(self, commit=True):
        thread = super().save(commit=False)
        if self.forum:
            thread.forum = self.forum
        if self.user:
            thread.author = self.user
        if commit:
            thread.save()
        return thread


class PostForm(forms.ModelForm):
    """Formulaire pour créer/modifier une réponse."""

    def __init__(self, *args, **kwargs):
        self.thread = kwargs.pop('thread', None)
        self.user = kwargs.pop('user', None)

        # Remove 'thread' from POST data if present (defensive)
        if args and hasattr(args[0], 'copy'):
            data = args[0]
            mutable = data.copy()
            if 'thread' in mutable:
                mutable.pop('thread')
            args = (mutable,) + args[1:]
        super().__init__(*args, **kwargs)

    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre réponse...',
            }),
        }
        labels = {
            'content': 'Réponse',
        }

    def clean(self):
        cleaned_data = super().clean()

        if not self.thread:
            raise ValidationError("Le thread est requis.")

        if self.user and not self.thread.forum.can_write(self.user):
            raise ValidationError("Vous n'avez pas la permission de répondre dans ce sujet.")

        return cleaned_data

    def save(self, commit=True):
        post = super().save(commit=False)
        post.thread = self.thread
        if self.user:
            post.author = self.user
        if commit:
            post.save()
        return post

class SurveyForm(forms.ModelForm):
    """Formulaire pour créer un sondage (US 10.2)"""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.forum = kwargs.pop('forum', None)
        super().__init__(*args, **kwargs)

        forums_qs = Forum.objects.all().select_related('club')
        if self.user and not self.user.is_superuser:
            access_q = Q(visibility='public') | Q(club__responsible=self.user) | Q(club__members=self.user)
            forums_qs = forums_qs.filter(access_q)

        if self.forum:
            self.fields['forum'].queryset = Forum.objects.filter(pk=self.forum.pk)
            self.fields['forum'].initial = self.forum
            self.fields['forum'].disabled = True
        else:
            self.fields['forum'].queryset = forums_qs.distinct()

    class Meta:
        model = Survey
        fields = ['title', 'description', 'forum', 'closes_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du sondage'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du sondage'}),
            'forum': forms.Select(attrs={'class': 'form-control'}),
            'closes_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Titre du sondage',
            'description': 'Description',
            'forum': 'Forum',
            'closes_at': 'Date de clôture (optionnel)',
        }

    def clean(self):
        cleaned_data = super().clean()
        forum = self.forum or cleaned_data.get('forum')

        if not forum:
            raise ValidationError(
                _("Un forum est requis pour créer un sondage."),
                code='missing_forum'
            )

        if self.user and not forum.can_write(self.user):
            raise ValidationError(
                _("Vous n'avez pas la permission de créer un sondage dans ce forum."),
                code='permission_denied'
            )

        self.forum = forum
        return cleaned_data


class SurveyOptionForm(forms.ModelForm):
    """Formulaire pour ajouter des options à un sondage (US 10.2)"""

    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop('survey', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = SurveyOption
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option de réponse',
                'hx-post': '/forum/check_option/',
                'hx-trigger': 'keyup changed delay:500ms',
                'hx-target': '#option-errors'
            }),
        }
        labels = {
            'text': 'Option',
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')

        if self.survey and text:
            if self.survey.options.filter(text__iexact=text).exists():
                raise ValidationError(
                    _('Cette option existe déjà pour ce sondage.'),
                    code='duplicate_option'
                )

        return text

    def save(self, commit=True):
        option = super().save(commit=False)
        if self.survey:
            option.survey = self.survey
        if commit:
            option.save()
        return option
