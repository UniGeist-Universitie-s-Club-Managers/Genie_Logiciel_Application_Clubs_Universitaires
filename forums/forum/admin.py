from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Club, Forum, Thread, Post, Survey, SurveyOption, SurveyVote, User


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'responsible', 'created_at')
    search_fields = ('name', 'responsible__username')
    filter_horizontal = ('members',)


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('title', 'visibility', 'club', 'created_by', 'created_at')
    list_filter = ('visibility', 'club', 'created_at')
    search_fields = ('title', 'description')
    list_select_related = ('club', 'created_by')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'forum', 'author', 'created_at')
    list_filter = ('forum', 'created_at')
    search_fields = ('title', 'content')
    list_select_related = ('forum', 'author')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'thread', 'author', 'created_at')
    list_filter = ('thread__forum', 'created_at')
    search_fields = ('content',)
    list_select_related = ('thread', 'author')
    
    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    truncated_content.short_description = 'Content'

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'forum', 'author', 'created_at', 'is_closed')
    list_filter = ('is_closed', 'forum', 'created_at')
    search_fields = ('title', 'description')
    list_select_related = ('forum', 'author')

@admin.register(SurveyOption)
class SurveyOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'vote_count')
    list_filter = ('survey',)
    
    def vote_count(self, obj):
        return obj.votes.count()
    vote_count.short_description = 'Votes'

@admin.register(SurveyVote)
class SurveyVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'survey', 'option', 'created_at')
    list_filter = ('created_at', 'survey')
    list_select_related = ('user', 'survey', 'option')
    search_fields = ('user__username', 'survey__title', 'option__text')

class CustomAdminSite(admin.AdminSite):
    site_header = "Mon Forum Admin"
    site_title = "Forum Admin"
    index_title = "Bienvenue sur le dashboard"

    class Media:
        css = {
            'all': ('css/theme.css',)  # chemin relatif à static/
        }

# Remplacer le site admin par défaut
admin_site = CustomAdminSite(name='myadmin')
class CustomAdminSite(admin.AdminSite):
    site_header = "Mon Forum Admin"
    site_title = "Forum Admin"
    index_title = "Bienvenue sur le dashboard"

    # Inclure le CSS personnalisé
    class Media:
        css = {
            'all': ('css/theme.css',)  # chemin relatif à static/
        }

# Créer l’instance de l’admin personnalisé
admin_site = CustomAdminSite(name='myadmin')

# Optionnel : UserAdmin avec CSS
class CustomUserAdmin(UserAdmin):
    class Media:
        css = {
            'all': ('css/theme.css',)
        }

# Désenregistrer l'ancien User et réenregistrer avec CustomUserAdmin
admin_site.register(User, CustomUserAdmin)

# ====== Remplacer le site admin par défaut pour tous les modèles ======
admin_site.register(Club, ClubAdmin)
admin_site.register(Forum, ForumAdmin)
admin_site.register(Thread, ThreadAdmin)
admin_site.register(Post, PostAdmin)
admin_site.register(Survey, SurveyAdmin)
admin_site.register(SurveyOption, SurveyOptionAdmin)
admin_site.register(SurveyVote, SurveyVoteAdmin)