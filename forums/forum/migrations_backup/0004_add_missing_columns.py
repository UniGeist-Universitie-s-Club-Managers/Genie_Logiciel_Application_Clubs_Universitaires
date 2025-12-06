# Generated manually to add missing columns and fix schema

from django.db import migrations


def migrate_forum_table_forward(apps, schema_editor):
    """Migrate forum_forum table: rename name->title, is_private->visibility, add club_id"""
    db_alias = schema_editor.connection.alias
    
    # SQLite doesn't support ALTER TABLE RENAME COLUMN directly, so we recreate
    with schema_editor.connection.cursor() as cursor:
        # Create temp table with new structure
        cursor.execute("""
            CREATE TABLE temp_forum_forum (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                visibility VARCHAR(10) NOT NULL DEFAULT 'public',
                club_id INTEGER,
                created_by_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        # Copy data: name->title, is_private->visibility
        cursor.execute("""
            INSERT INTO temp_forum_forum (id, title, description, visibility, club_id, created_by_id, created_at, updated_at)
            SELECT 
                id,
                name as title,
                description,
                CASE WHEN is_private = 1 THEN 'private' ELSE 'public' END as visibility,
                NULL as club_id,
                created_by_id,
                created_at,
                updated_at
            FROM forum_forum
        """)
        
        # Drop old table and rename
        cursor.execute("DROP TABLE forum_forum")
        cursor.execute("ALTER TABLE temp_forum_forum RENAME TO forum_forum")


def migrate_forum_table_backward(apps, schema_editor):
    """Reverse migration"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE temp_forum_forum (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                is_private INTEGER NOT NULL DEFAULT 0,
                created_by_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)
        
        cursor.execute("""
            INSERT INTO temp_forum_forum (id, name, description, is_private, created_by_id, created_at, updated_at)
            SELECT 
                id,
                title as name,
                description,
                CASE WHEN visibility = 'private' THEN 1 ELSE 0 END as is_private,
                created_by_id,
                created_at,
                updated_at
            FROM forum_forum
        """)
        
        cursor.execute("DROP TABLE forum_forum")
        cursor.execute("ALTER TABLE temp_forum_forum RENAME TO forum_forum")


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_add_thread_pinned_closed'),
    ]

    operations = [
        migrations.RunPython(migrate_forum_table_forward, migrate_forum_table_backward),
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

