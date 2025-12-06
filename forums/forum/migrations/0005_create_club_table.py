from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('forum', '0004_add_missing_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS forum_club (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    responsible_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                );
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS forum_club;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS forum_club_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    club_id INTEGER NOT NULL REFERENCES forum_club(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE
                );

                CREATE UNIQUE INDEX IF NOT EXISTS forum_club_members_club_user_idx
                ON forum_club_members(club_id, user_id);
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS forum_club_members;
            """,
        ),
    ]

