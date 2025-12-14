from .models import Notification


def unread_notifications(request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}
    count = Notification.objects.filter(recipient=user, read=False).count()
    recent = Notification.objects.filter(recipient=user).order_by('-created_at')[:5]
    return {'unread_notifications_count': count, 'recent_notifications': recent}
