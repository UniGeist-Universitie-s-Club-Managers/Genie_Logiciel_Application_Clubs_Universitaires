# forum/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import ThreadForm, PostForm, ForumForm, SurveyForm, SurveyOptionForm
from .models import Thread, Post, Forum, Survey, SurveyOption, SurveyVote
from .models import Notification
from .utils import (
    get_forum_or_404,
    get_thread_or_404,
    get_post_or_404,
    get_survey_or_404,
)
from django.shortcuts import get_object_or_404, redirect, render
from .models import Thread, Post
from .forms import PostForm

def thread_detail(request, pk):
    thread = get_object_or_404(Thread, pk=pk)
    posts = thread.posts.all()  # récupère tous les posts de ce thread

    if request.method == 'POST':
        # Debug: inspect POST keys
        try:
            print("thread_detail POST keys before cleaning:", list(request.POST.keys()))
        except Exception:
            pass

        post_data = request.POST.copy()
        post_data.pop('thread', None)

        try:
            form = PostForm(post_data, thread=thread, user=request.user)
        except ValueError as e:
            # Log full keys/values for diagnosis and try a more aggressive clean
            try:
                print("ValueError creating PostForm:", e)
                print("POST items:")
                for k, v in request.POST.items():
                    print(k, '->', v)
            except Exception:
                pass

            # Remove any unexpected keys and retry
            cleaned = {k: v for k, v in request.POST.items() if k in ('content', 'csrfmiddlewaretoken')}
            form = PostForm(cleaned, thread=thread, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            return redirect('forum:thread-detail', pk=thread.pk)
    else:
        form = PostForm(thread=thread, user=request.user)

    context = {
        'thread': thread,
        'posts': posts,
        'form': form,
        'can_reply': True,  # selon ta logique de permission
    }
    return render(request, 'forum/thread_detail.html', context)


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'forum/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.read = True
    notif.save()
    # redirect to appropriate target
    if notif.post:
        return redirect('forum:thread-detail', pk=notif.post.thread.pk)
    if notif.survey:
        return redirect('forum:survey-detail', pk=notif.survey.pk)
    return redirect('forum:thread-list')

def survey_vote(request, pk):
    """Permet à un utilisateur de voter pour une option d'un sondage"""
    if not request.user.is_authenticated:
        messages.error(request, "Tu dois être connecté(e) pour voter.")
        return redirect('login')

    survey = get_object_or_404(Survey, pk=pk)

    if not survey.can_vote(request.user):
        messages.error(request, "Vous ne pouvez pas voter pour ce sondage.")
        return redirect(survey.get_absolute_url())

    option_pk = request.POST.get('option')
    if not option_pk:
        messages.error(request, "Veuillez sélectionner une option pour voter.")
        return redirect(survey.get_absolute_url())

    option = get_object_or_404(SurveyOption, pk=option_pk, survey=survey)

    # Créer ou modifier le vote (upsert)
    vote, created = SurveyVote.objects.get_or_create(survey=survey, user=request.user, defaults={'option': option})
    if not created:
        if vote.option_id == option.pk:
            messages.info(request, "Tu as déjà voté pour cette option.")
        else:
            vote.option = option
            vote.save()
            messages.success(request, f"Ton vote a été modifié pour '{option.text}'.")
    else:
        messages.success(request, f"Merci pour ton vote pour '{option.text}' !")
    return redirect(survey.get_absolute_url())


def add_survey_option(request, pk):
    """Permet à l'auteur/staff/responsable du club d'ajouter des options à un sondage"""
    if not request.user.is_authenticated:
        messages.error(request, "Tu dois être connecté(e) pour ajouter une option.")
        return redirect('login')

    survey = get_object_or_404(Survey, pk=pk)
    if not survey.can_manage(request.user):
        messages.error(request, "Vous n'avez pas la permission d'ajouter des options à ce sondage.")
        return redirect(survey.get_absolute_url())

    if request.method == 'POST':
        form = SurveyOptionForm(request.POST, survey=survey, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Option ajoutée avec succès.")
        else:
            for err in form.errors.values():
                messages.error(request, err)
    return redirect(survey.get_absolute_url())


def survey_option_voters(request, survey_pk, option_pk):
    """Affiche la liste des utilisateurs ayant voté pour une option donnée."""
    survey = get_object_or_404(Survey, pk=survey_pk)
    if not survey.can_view(request.user):
        messages.error(request, "Vous n'avez pas accès à ce sondage.")
        return redirect(survey.get_absolute_url())

    option = get_object_or_404(SurveyOption, pk=option_pk, survey=survey)
    votes = option.votes.select_related('user').order_by('created_at')
    voters = [v.user for v in votes]

    return render(request, 'forum/survey_option_voters.html', {
        'survey': survey,
        'option': option,
        'voters': voters,
    })

def _forum_visibility_q(user):
    if not user.is_authenticated:
        return Q(visibility='public')
    if user.is_superuser:
        return Q()
    return (
        Q(visibility='public')
        | Q(visibility='private', club__responsible=user)
        | Q(visibility='private', club__members=user)
    )


def _thread_visibility_q(user):
    if not user.is_authenticated:
        return Q(forum__visibility='public')
    if user.is_superuser:
        return Q()
    return (
        Q(forum__visibility='public')
        | Q(forum__visibility='private', forum__club__responsible=user)
        | Q(forum__visibility='private', forum__club__members=user)
    )

# ---------- Thread list ----------
class ThreadListView(LoginRequiredMixin, ListView):
    model = Thread
    template_name = 'forum/thread_list.html'
    context_object_name = 'threads'
    paginate_by = 10

    def get_queryset(self):
        qs = Thread.objects.select_related('forum', 'forum__club', 'author')
        qs = qs.filter(_thread_visibility_q(self.request.user))
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(body__icontains=query))
        return super().get_queryset().select_related('author', 'forum')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user  # Passe l'utilisateur connecté au contexte
        return context
    def _user_can_create_thread(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        forums = Forum.objects.select_related('club')
        return any(forum.can_write(user) for forum in forums)

# ---------- Thread detail (GET + POST pour réponse) ----------
from django.views.generic import DetailView
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Thread
from .forms import PostForm

class ThreadDetailView(DetailView):
    model = Thread
    template_name = 'forum/thread_detail.html'
    context_object_name = 'thread'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.can_view(self.request.user):
            raise PermissionDenied("Accès refusé à ce sujet.")
        # Attributs sûrs pour le template
        obj.can_edit_thread = obj.can_edit(self.request.user)
        obj.can_delete_thread = obj.can_delete(self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread = self.object
        can_reply = thread.forum.can_write(self.request.user)
        context['can_reply'] = can_reply

        if can_reply:
            context['form'] = PostForm(thread=thread, user=self.request.user)
        
        posts = list(thread.posts.select_related('author').order_by('created_at'))
        for post in posts:
            # Attributs sûrs pour le template
            post.can_edit = post.can_edit(self.request.user)
            post.can_delete = post.can_delete(self.request.user)
        context['posts'] = posts
        return context

    def post(self, request, *args, **kwargs):
        # Handle POST to create a reply (keeps behavior aligned with function-based view)
        if not request.user.is_authenticated:
            messages.error(request, "Tu dois être connecté(e) pour répondre.")
            return redirect('login')

        self.object = self.get_object()
        if not self.object.forum.can_write(request.user):
            raise PermissionDenied("Vous ne pouvez pas répondre dans ce forum.")

        # copy POST and remove any stray 'thread' key
        post_data = request.POST.copy()
        post_data.pop('thread', None)

        try:
            if request.FILES:
                form = PostForm(post_data, request.FILES, thread=self.object, user=request.user)
            else:
                form = PostForm(post_data, thread=self.object, user=request.user)
        except ValueError:
            cleaned = {k: v for k, v in request.POST.items() if k in ('content', 'csrfmiddlewaretoken')}
            form = PostForm(cleaned, thread=self.object, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Ta réponse a été publiée.")
            return redirect(reverse('forum:thread-detail', kwargs={'pk': self.object.pk}))
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context)


# ---------- Thread create ----------
class ThreadCreateView(LoginRequiredMixin, CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = 'forum/thread_form.html'
    success_url = reverse_lazy('forum:thread-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        forum_pk = self.kwargs.get('forum_pk') or self.request.GET.get('forum')
        if forum_pk:
            kwargs['forum'] = get_forum_or_404(forum_pk, self.request.user)
        return kwargs

    def form_valid(self, form):
        forum = form.forum or form.cleaned_data.get('forum')
        if not forum.can_write(self.request.user):
            raise PermissionDenied("Vous ne pouvez pas créer de sujet dans ce forum.")
        form.instance.author = self.request.user
        form.instance.forum = forum
        messages.success(self.request, "Sujet créé avec succès.")
        return super().form_valid(form)
# ---------- Thread update ----------
class ThreadUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Thread
    form_class = ThreadForm
    template_name = 'forum/thread_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['forum'] = self.get_object().forum
        return kwargs

    def test_func(self):
        thread = self.get_object()
        return thread.can_edit(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Tu n'as pas la permission de modifier ce sujet.")
        return redirect('forum:thread-detail', pk=self.get_object().pk)

# ---------- Thread delete ----------
class ThreadDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Thread
    template_name = 'forum/thread_confirm_delete.html'
    success_url = reverse_lazy('forum:thread-list')

    def test_func(self):
        thread = self.get_object()
        return thread.can_delete(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Tu n'as pas la permission de supprimer ce sujet.")
        return redirect('forum:thread-detail', pk=self.get_object().pk)
# ---------- Post update ----------
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'forum/post_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['thread'] = self.get_object().thread
        return kwargs

    def test_func(self):
        post = self.get_object()
        return post.can_edit(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Tu n'as pas la permission de modifier cette réponse.")
        post = self.get_object()
        return redirect('forum:thread-detail', pk=post.thread.pk)

    def get_success_url(self):
        messages.success(self.request, "Réponse modifiée avec succès.")
        return reverse('forum:thread-detail', kwargs={'pk': self.object.thread.pk})

# ---------- Post delete ----------
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'forum/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        return post.can_delete(self.request.user)

    def handle_no_permission(self):
        messages.error(self.request, "Tu n'as pas la permission de supprimer cette réponse.")
        post = self.get_object()
        return redirect('forum:thread-detail', pk=post.thread.pk)

    def get_success_url(self):
        messages.success(self.request, "Réponse supprimée avec succès.")
        return reverse('forum:thread-detail', kwargs={'pk': self.object.thread.pk})

# ========== FORUM CRUD (US 9.1, 9.2, 7.3) ==========

class ForumListView(ListView):
    """Liste de tous les forums (US 7.3)"""
    model = Forum
    template_name = 'forum/forum_list.html'
    context_object_name = 'forums'
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset().select_related('club', 'created_by')
        return qs.filter(_forum_visibility_q(self.request.user)).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forums = list(context['forums'])
        for forum in forums:
            forum._can_manage = forum.can_manage(self.request.user)
        context['forums'] = forums
        context['object_list'] = forums
        return context


class ForumDetailView(DetailView):
    """Détail d'un forum avec ses threads et sondages"""
    model = Forum
    template_name = 'forum/forum_detail.html'
    context_object_name = 'forum'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.can_read(self.request.user):
            raise PermissionDenied("Accès refusé à ce forum.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['threads'] = self.object.threads.select_related('author').order_by('-created_at')[:10]
        context['surveys'] = self.object.surveys.select_related('author').order_by('-created_at')[:5]
        context['can_write_forum'] = self.object.can_write(self.request.user)
        context['can_manage_forum'] = self.object.can_manage(self.request.user)
        return context


class ForumCreateView(LoginRequiredMixin, CreateView):
    """Créer un forum (US 9.1 pour admin, 9.2 pour responsable)"""
    model = Forum
    form_class = ForumForm
    template_name = 'forum/forum_form.html'
    success_url = reverse_lazy('forum:forum-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not (self.request.user.is_superuser or form.cleaned_data.get('visibility') == 'public'):
            club = form.cleaned_data.get('club')
            if not club or club.responsible != self.request.user:
                raise PermissionDenied("Vous ne pouvez pas créer ce forum privé.")
        form.instance.created_by = self.request.user
        messages.success(self.request, "Forum créé avec succès.")
        return super().form_valid(form)


class ForumUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Modifier un forum"""
    model = Forum
    form_class = ForumForm
    template_name = 'forum/forum_form.html'

    def test_func(self):
        forum = self.get_object()
        return forum.can_manage(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Forum modifié avec succès.")
        return super().form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, "Tu n'as pas la permission de modifier ce forum.")
        return redirect('forum:forum-detail', pk=self.get_object().pk)


class ForumDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Supprimer un forum"""
    model = Forum
    template_name = 'forum/forum_confirm_delete.html'
    success_url = reverse_lazy('forum:forum-list')

    def test_func(self):
        forum = self.get_object()
        return forum.can_manage(self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Forum supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        messages.error(self.request, "Tu n'as pas la permission de supprimer ce forum.")
        return redirect('forum:forum-detail', pk=self.get_object().pk)


# ========== SURVEY CRUD (US 10.2) ==========

class SurveyListView(ListView):
    """Liste de tous les sondages"""
    model = Survey
    template_name = 'forum/survey_list.html'
    context_object_name = 'surveys'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related('forum', 'forum__club', 'author')
        return qs.filter(_thread_visibility_q(self.request.user)).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surveys = list(context['surveys'])
        for survey in surveys:
            survey._can_manage_for_user = survey.can_manage(self.request.user)
        context['surveys'] = surveys
        context['object_list'] = surveys
        context['can_create_survey'] = self._user_can_create_survey()
        return context

    def _user_can_create_survey(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        forums = Forum.objects.select_related('club')
        return any(forum.can_write(user) for forum in forums)


class SurveyDetailView(DetailView):
    model = Survey
    template_name = 'forum/survey_detail.html'
    context_object_name = 'survey'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.get_object()
        user = self.request.user
        
        context['can_vote'] = survey.can_vote(user)
        user_vote = survey.votes.filter(user=user).first()
        context['user_has_voted'] = bool(user_vote)
        context['user_vote'] = user_vote.option.pk if user_vote else None
        context['options_with_votes'] = self.get_options_with_votes(survey)
        context['total_votes'] = survey.votes.count()
        context['can_manage_survey'] = survey.can_manage(user)
        
        return context

    def get_options_with_votes(self, survey):
        options = survey.options.all()
        total_votes = survey.votes.count()
        
        return [{
            'option': option,
            'vote_count': option.votes.count(),
            'percentage': round(option.votes.count() / total_votes * 100, 1) if total_votes > 0 else 0
        } for option in options]
class SurveyCreateView(CreateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'forum/survey_form.html'
    success_url = reverse_lazy('forum:survey-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Sondage créé avec succès.")
        return super().form_valid(form)

class SurveyUpdateView(UpdateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'forum/survey_form.html'
    success_url = reverse_lazy('forum:survey-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class SurveyDeleteView(DeleteView):
    model = Survey
    template_name = 'forum/survey_confirm_delete.html'
    success_url = reverse_lazy('forum:survey-list')
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages

def signup(request):
    """Inscription d'un nouvel utilisateur"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue sur notre forum.")
            return redirect('forum:thread-list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})