from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_add_missing_fields'),  # Utilisez le bon nom de migration précédente
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='is_pinned',
            field=models.BooleanField(default=False, verbose_name='Épinglé'),
        ),
        migrations.AddField(
            model_name='thread',
            name='is_closed',
            field=models.BooleanField(default=False, verbose_name='Fermé'),
        ),
    ]