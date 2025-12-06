from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('forum', '0007_copy_club_relation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forum',
            name='club',
        ),
        migrations.RenameField(
            model_name='forum',
            old_name='club_private',
            new_name='club',
        ),
    ]

