from django.contrib import admin

from .models import Aid, AidRequest, Category, Club, Resource, FAQ, Favorite


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "description")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "club",
        "submitted_by",
        "is_validated",
        "date_submitted",
    )
    search_fields = ("title", "category__name", "submitted_by__username")
    list_filter = ("category", "club", "is_validated", "date_submitted")
    list_editable = ("is_validated",)
    readonly_fields = ("date_submitted",)


@admin.register(Aid)
class AidAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "club",
        "submitted_by",
        "is_validated",
        "date_submitted",
    )
    search_fields = ("title", "category__name", "submitted_by__username")
    list_filter = ("category", "club", "is_validated", "date_submitted")
    list_editable = ("is_validated",)
    readonly_fields = ("date_submitted",)


@admin.register(AidRequest)
class AidRequestAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "requested_by",
        "status",
        "date_requested",
    )
    search_fields = ("description", "requested_by__username")
    list_filter = ("type", "status", "date_requested")
    readonly_fields = ("date_requested",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "created_at", "updated_at")
    search_fields = ("question", "answer")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "resource", "aid", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "resource__title", "aid__title")
    readonly_fields = ("created_at",)
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "resource", "aid")


# Customize Django Admin site
admin.site.site_header = "Resources/Aids"
admin.site.site_title = "Resources/Aids Admin Portal"
admin.site.index_title = "Welcome to the Resources/Aids Management System"
