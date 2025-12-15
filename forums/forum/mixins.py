from django.core.exceptions import PermissionDenied

from .utils import get_forum_or_404


class ForumPermissionMixin:
    """Mixin pour charger un forum en vérifiant les droits de lecture."""

    forum_url_kwarg = 'forum_pk'

    def get_forum_pk(self):
        return self.kwargs.get(self.forum_url_kwarg)

    def get_forum(self):
        forum_pk = self.get_forum_pk()
        if forum_pk is None:
            raise PermissionDenied("Forum introuvable.")
        return get_forum_or_403(forum_pk, self.request.user)

    def dispatch(self, request, *args, **kwargs):
        self.forum = self.get_forum()
        return super().dispatch(request, *args, **kwargs)


class ForumWriteRequiredMixin(ForumPermissionMixin):
    """Mixin qui exige une permission d'écriture sur le forum chargé."""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not self.forum.can_write(request.user):
            raise PermissionDenied("Vous n'avez pas la permission d'écrire dans ce forum.")
        return response

