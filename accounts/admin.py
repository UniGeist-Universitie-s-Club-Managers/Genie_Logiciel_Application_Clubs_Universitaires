# accounts/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Badge, Club, Membership, Event, EventParticipation, Contribution, UserBadge

User = get_user_model()

# User personnalisé
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'address', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_active', 'is_staff')

# Badges
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon')
    search_fields = ('name',)

# Clubs
@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Memberships
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'role', 'active', 'joined_at')
    list_filter = ('role', 'active')
    search_fields = ('user__username', 'club__name')

# Events
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'start', 'end')
    list_filter = ('club',)
    search_fields = ('title',)

# Event participations
@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registered_at', 'attended')
    list_filter = ('attended',)
    search_fields = ('user__username', 'event__title')

# Contributions
@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'club', 'score', 'created_at')
    list_filter = ('club',)
    search_fields = ('title', 'user__username')

# UserBadge
@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at')
    search_fields = ('user__username', 'badge__name')
