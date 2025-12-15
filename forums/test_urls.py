"""
Script de test rapide pour vérifier toutes les URLs du forum
Exécuter avec: python manage.py shell < test_urls.py
"""

from django.urls import reverse
from django.contrib.auth.models import User
from forum.models import Forum, Thread, Post, Survey

print("\n" + "="*60)
print("🧪 TEST DES URLs DU FORUM")
print("="*60 + "\n")

# Test des URLs sans paramètres
urls_sans_params = [
    ('forum:thread-list', 'Liste des threads'),
    ('forum:forum-list', 'Liste des forums'),
    ('forum:forum-create', 'Créer un forum'),
    ('forum:thread-create', 'Créer un thread'),
    ('forum:survey-list', 'Liste des sondages'),
    ('forum:survey-create', 'Créer un sondage'),
]

print("📋 URLs sans paramètres:")
print("-" * 60)
for url_name, description in urls_sans_params:
    try:
        url = reverse(url_name)
        print(f"✅ {description:30} → {url}")
    except Exception as e:
        print(f"❌ {description:30} → ERREUR: {e}")

# Test des URLs avec paramètres (si des objets existent)
print("\n📋 URLs avec paramètres (ID=1):")
print("-" * 60)

urls_avec_params = [
    ('forum:forum-detail', 'Détail forum', {'pk': 1}),
    ('forum:forum-update', 'Modifier forum', {'pk': 1}),
    ('forum:forum-delete', 'Supprimer forum', {'pk': 1}),
    ('forum:thread-detail', 'Détail thread', {'pk': 1}),
    ('forum:thread-update', 'Modifier thread', {'pk': 1}),
    ('forum:thread-delete', 'Supprimer thread', {'pk': 1}),
    ('forum:post-update', 'Modifier post', {'pk': 1}),
    ('forum:post-delete', 'Supprimer post', {'pk': 1}),
    ('forum:survey-detail', 'Détail sondage', {'pk': 1}),
    ('forum:survey-update', 'Modifier sondage', {'pk': 1}),
    ('forum:survey-delete', 'Supprimer sondage', {'pk': 1}),
]

for url_name, description, kwargs in urls_avec_params:
    try:
        url = reverse(url_name, kwargs=kwargs)
        print(f"✅ {description:30} → {url}")
    except Exception as e:
        print(f"❌ {description:30} → ERREUR: {e}")

# Statistiques de la base de données
print("\n📊 Statistiques de la base de données:")
print("-" * 60)
print(f"👥 Utilisateurs: {User.objects.count()}")
print(f"🏛️  Forums: {Forum.objects.count()}")
print(f"📝 Threads: {Thread.objects.count()}")
print(f"💬 Posts: {Post.objects.count()}")
print(f"📊 Sondages: {Survey.objects.count()}")

print("\n" + "="*60)
print("✅ Test terminé !")
print("="*60 + "\n")
