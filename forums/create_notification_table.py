import sqlite3
conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS forum_notification (
    id integer primary key autoincrement,
    notif_type varchar(20) not null,
    message varchar(255) not null,
    read integer not null default 0,
    created_at datetime not null default (CURRENT_TIMESTAMP),
    actor_id integer,
    recipient_id integer not null,
    thread_id integer,
    post_id integer,
    survey_id integer,
    option_id integer,
    FOREIGN KEY(actor_id) REFERENCES auth_user(id) ON DELETE SET NULL,
    FOREIGN KEY(recipient_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY(thread_id) REFERENCES forum_thread(id) ON DELETE CASCADE,
    FOREIGN KEY(post_id) REFERENCES forum_post(id) ON DELETE CASCADE,
    FOREIGN KEY(survey_id) REFERENCES forum_survey(id) ON DELETE CASCADE,
    FOREIGN KEY(option_id) REFERENCES forum_surveyoption(id) ON DELETE CASCADE
);''')
conn.commit()
print('Created table forum_notification')
# Insert migration record into django_migrations
c.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('forum','0010_create_notification', datetime('now'))")
conn.commit()
print('Marked migration 0010_create_notification as applied')
conn.close()
