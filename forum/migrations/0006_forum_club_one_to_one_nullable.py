from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('forum', '0005_create_club_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='forum',
            name='club_private',
            field=models.OneToOneField(
                to='forum.club',
                on_delete=models.CASCADE,
                related_name='private_forum_temp',
                null=True,
                blank=True,
            ),
        ),
    ]

