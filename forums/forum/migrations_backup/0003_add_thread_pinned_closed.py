# Generated manually to add missing fields to existing table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # SQLite: Add columns directly
            sql=[
                "ALTER TABLE forum_thread ADD COLUMN is_pinned INTEGER NOT NULL DEFAULT 0;",
                "ALTER TABLE forum_thread ADD COLUMN is_closed INTEGER NOT NULL DEFAULT 0;",
            ],
            reverse_sql=[
                # Note: SQLite doesn't support DROP COLUMN easily, so we'll leave it
                # If you need to reverse, you'd need to recreate the table
            ],
        ),
    ]

