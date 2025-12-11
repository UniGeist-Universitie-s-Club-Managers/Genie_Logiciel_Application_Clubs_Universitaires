# Generated manually to add missing columns

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Add is_closed to forum_survey if it doesn't exist
            sql="ALTER TABLE forum_survey ADD COLUMN is_closed INTEGER NOT NULL DEFAULT 0;",
            reverse_sql=[],
        ),
        migrations.RunSQL(
            # Add is_modified to forum_post if it doesn't exist
            sql="ALTER TABLE forum_post ADD COLUMN is_modified INTEGER NOT NULL DEFAULT 0;",
            reverse_sql=[],
        ),
    ]

