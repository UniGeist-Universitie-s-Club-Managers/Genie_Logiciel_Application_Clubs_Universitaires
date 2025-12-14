from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('forum', '0002_initial'),  # Ensure this runs after the initial migration that creates Thread
    ]

    operations = [
        # No-op: fields are present in the initial migration already.
    ]