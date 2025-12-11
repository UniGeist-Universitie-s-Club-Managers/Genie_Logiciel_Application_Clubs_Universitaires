from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# -------------------------
# Utilisateur personnalisé
# -------------------------
class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


# -------------------------
# Badges
# -------------------------
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=200, blank=True, help_text="URL/icon name (optional)")

    def __str__(self):
        return self.name


# -------------------------
# Clubs
# -------------------------
class Club(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# -------------------------
# Membership (adhésion)
# -------------------------
class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=50, default='member')  # member | admin | moderator
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user} ➜ {self.club} ({self.role})"


# -------------------------
# Events
# -------------------------
class Event(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self):
        return f"{self.title} ({self.club})"


class EventParticipation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_participations')
    registered_at = models.DateTimeField(default=timezone.now)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user} - {self.event.title}"


# -------------------------
# Contributions
# -------------------------
class Contribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='contributions', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    score = models.IntegerField(default=0)  # points for contribution (to award badges)

    def __str__(self):
        return f"{self.title} by {self.user}"


# -------------------------
# Relation User <-> Badge
# -------------------------
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user} earned {self.badge}"


# -------------------------
# Historique d'adhésion et contributions
# -------------------------
class MembershipHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_history')
    action = models.CharField(max_length=255)  # ex: "Rejoint le club X", "Contribution Y"
    club = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.action} ({self.date.strftime('%Y-%m-%d %H:%M')})"
