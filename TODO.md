# Plan d'intégration du dossier forums/forum/ au projet principal

## Étapes à suivre :
- [x] Modifier INSTALLED_APPS dans settings.py : remplacer 'forum' par 'forums.forum'
- [x] Modifier urls.py : remplacer include('forum.urls') par include('forums.forum.urls')
- [ ] Vérifier et mettre à jour les imports dans les fichiers de l'application forum si nécessaire
- [x] Exécuter les migrations pour s'assurer que la base de données est à jour
- [ ] Tester l'application pour vérifier que tout fonctionne

## Fichiers dépendants :
- university_project/settings.py
- university_project/urls.py
- Potentiellement des imports dans forums/forum/views.py ou autres fichiers de l'app

## Étapes de suivi :
- Après modifications, exécuter python manage.py makemigrations et migrate
- Tester l'accès aux URLs du forum
- Vérifier qu'aucune erreur n'apparaît dans les logs

# Remplacement de l'API OpenAI par Google Gemini

## Étapes à suivre :
- [x] Installer la bibliothèque google-generativeai
- [x] Modifier accounts/views.py pour remplacer les appels OpenAI par Google Gemini
- [x] Vérifier que GOOGLE_API_KEY est configuré dans settings.py
- [x] Tester le chatbot pour s'assurer que les recommandations fonctionnent

## Fichiers dépendants :
- accounts/views.py
- university_project/settings.py

## Étapes de suivi :
- [x] Tester le chatbot avec des questions de recommandation
- [x] Vérifier que les réponses sont en français
- [x] S'assurer que les erreurs sont gérées correctement
