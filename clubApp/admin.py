from django.contrib import admin
from .models import Club, Demande_creation_club


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'established_date')
    search_fields = ('name', 'description')
    list_filter = ('established_date',)
    list_per_page = 10
    readonly_fields = ('club_id',)

class DemandeCreationClubAdmin(admin.ModelAdmin):
    list_display = ('club_name', 'president_name', 'vice_president_name', 'requested_by')
    search_fields = ('club_name', 'president_name', 'vice_president_name', 'requested_by')
    list_per_page = 10
    readonly_fields = ('demande_id',)

# Register your models here.
admin.site.register(Club, ClubAdmin)
admin.site.register(Demande_creation_club, DemandeCreationClubAdmin)
