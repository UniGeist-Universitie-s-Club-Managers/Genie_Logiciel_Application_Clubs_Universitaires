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
