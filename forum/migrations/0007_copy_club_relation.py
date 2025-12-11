from django.db import migrations


def copy_fk_to_one_to_one(apps, schema_editor):
    Forum = apps.get_model('forum', 'Forum')
    for forum in Forum.objects.exclude(club__isnull=True):
        forum.club_private = forum.club
        forum.save(update_fields=['club_private'])


def reverse_func(apps, schema_editor):
    Forum = apps.get_model('forum', 'Forum')
    for forum in Forum.objects.exclude(club_private__isnull=True):
        forum.club = forum.club_private
        forum.save(update_fields=['club'])


class Migration(migrations.Migration):
    dependencies = [
        ('forum', '0006_forum_club_one_to_one_nullable'),
    ]

    operations = [
        migrations.RunPython(copy_fk_to_one_to_one, reverse_func),
    ]

