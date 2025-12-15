from django.apps import AppConfig


class ForumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'forums.forum'

    def ready(self):
        # Import signals to ensure they are registered
        try:
            import forums.forum.signals  # noqa: F401
        except Exception:
            pass
