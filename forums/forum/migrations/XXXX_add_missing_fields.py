# forum/migrations/XXXX_add_missing_fields.py
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

def set_default_values(apps, schema_editor):
    Thread = apps.get_model('forum', 'Thread')
    # Mettre à jour les enregistrements existants
    Thread.objects.filter(is_pinned__isnull=True).update(is_pinned=False)
    Thread.objects.filter(is_closed__isnull=True).update(is_closed=False)

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_initial'),  # Run after initial migration
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # No-op: thread pinned/closed fields are created in the initial migration.
        # RunPython kept for history but won't be executed on fresh DBs.
        migrations.RunPython(set_default_values),
    ]