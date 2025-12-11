from .models import Aid, Notification, Resource


def create_validation_notification(resource=None, aid=None, user=None):
    """Crée une notification lorsqu'une ressource ou aide est validée."""
    if not user:
        return None
    
    if resource:
        notification = Notification.objects.create(
            user=user,
            type=Notification.TYPE_VALIDATION,
            title=f"Ressource validée : {resource.title}",
            message=f"Votre ressource '{resource.title}' a été validée par un administrateur et est maintenant visible par tous les membres.",
            resource=resource,
        )
        return notification
    elif aid:
        notification = Notification.objects.create(
            user=user,
            type=Notification.TYPE_VALIDATION,
            title=f"Aide validée : {aid.title}",
            message=f"Votre aide '{aid.title}' a été validée par un administrateur et est maintenant visible par tous les membres.",
            aid=aid,
        )
        return notification
    return None


def create_request_notification(request, approved=True):
    """Crée une notification lorsqu'une demande est approuvée ou rejetée."""
    if approved:
        notification = Notification.objects.create(
            user=request.applicant,
            type=Notification.TYPE_REQUEST_APPROVED,
            title=f"Demande approuvée",
            message=f"Votre demande '{getattr(request, 'title', request.aid.title if hasattr(request, 'aid') else '')}' a été approuvée.",
        )
    else:
        notification = Notification.objects.create(
            user=request.applicant,
            type=Notification.TYPE_REQUEST_REJECTED,
            title=f"Demande rejetée",
            message=f"Votre demande '{getattr(request, 'title', request.aid.title if hasattr(request, 'aid') else '')}' a été rejetée.",
        )
    return notification


