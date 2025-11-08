from django.contrib import admin
from .models import Club


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'established_date')
    search_fields = ('name',)
    list_filter = ('established_date',)
    list_per_page = 10
    readonly_fields = ('club_id',)
# Register your models here.
admin.site.register(Club, ClubAdmin)
