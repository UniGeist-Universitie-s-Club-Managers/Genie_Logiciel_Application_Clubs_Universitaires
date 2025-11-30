# 🆘 Troubleshooting - Guide de Dépannage

## Problèmes Courants et Solutions

### 1. **Les CSS ne s'affichent pas**

#### ❌ Problème
Les pages HTML s'affichent sans styles, texte blanc sur fond blanc, etc.

#### ✅ Solutions

1. **Vérifier le chargement des static files** :
   ```bash
   python manage.py collectstatic
   python manage.py runserver
   ```

2. **Vérifier la configuration dans `settings.py`** :
   ```python
   STATIC_URL = '/static/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
   DEBUG = True  # En développement
   ```

3. **Vérifier les chemins dans base.html** :
   ```html
   {% load static %}
   <link rel="stylesheet" href="{% static 'css/style.css' %}">
   <link rel="stylesheet" href="{% static 'css/theme.css' %}">
   ```

4. **Vider le cache du navigateur** :
   - Ctrl + Shift + R (Hard refresh)
   - Ou F12 → Network → Disable cache (cocher)

5. **Vérifier les erreurs en console** :
   - F12 → Console → Vérifier les erreurs rouges
   - F12 → Network → Vérifier si CSS/JS charge (200 status)

---

### 2. **Les icônes Font Awesome ne s'affichent pas**

#### ❌ Problème
Les icônes affichent des carrés vides ou caractères bizarres.

#### ✅ Solutions

1. **Vérifier le lien CDN dans base.html** :
   ```html
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
   ```

2. **Vérifier que vous utilisez la bonne classe** :
   ```html
   <!-- ✅ Correct -->
   <i class="fas fa-user"></i>
   
   <!-- ❌ Incorrect -->
   <i class="fa fa-user"></i>
   <i class="icon-user"></i>
   ```

3. **Vérifier la connexion Internet** :
   - CDN requires internet connection
   - Ou télécharger Font Awesome locally

4. **Actualiser le cache** :
   - Ctrl + Shift + R
   - Ctrl + F5

---

### 3. **Le style de la navbar ne fonctionne pas**

#### ❌ Problème
La navbar est visible mais pas stylisée correctement, couleurs manquantes, etc.

#### ✅ Solutions

1. **Vérifier les classes Bootstrap** :
   ```html
   <!-- Vérifier que c'est navbar-light, pas navbar-dark -->
   <nav class="navbar navbar-expand-lg navbar-light fixed-top minimalist-navbar">
   ```

2. **Vérifier le CSS personnalisé** :
   ```css
   .minimalist-navbar {
       background: rgba(255, 255, 255, 0.98) !important;
       backdrop-filter: blur(25px) !important;
   }
   ```

3. **Vérifier l'ordre des CSS** :
   - Bootstrap CSS doit être avant le CSS personnalisé
   - Dans base.html : Bootstrap → Font Awesome → style.css → theme.css

4. **Tester avec d'autres composants** :
   - Vérifier si d'autres éléments sont stylisés
   - Si non, c'est un problème global de CSS

---

### 4. **Les formulaires ne valident pas correctement**

#### ❌ Problème
Validation échouée, messages d'erreur ne s'affichent pas, ou validation incorrecte.

#### ✅ Solutions

1. **Vérifier le formulaire Django** :
   ```python
   # forms.py
   from django import forms
   
   class MyForm(forms.ModelForm):
       class Meta:
           model = MyModel
           fields = '__all__'
   ```

2. **Vérifier le template** :
   ```django
   <form method="post" class="needs-validation">
       {% csrf_token %}
       {% for field in form %}
           <div class="mb-3">
               <label class="form-label">{{ field.label }}</label>
               <input class="form-control {% if field.errors %}is-invalid{% endif %}" 
                      type="text" name="{{ field.name }}">
               {% if field.errors %}
                   <div class="invalid-feedback">{{ field.errors }}</div>
               {% endif %}
           </div>
       {% endfor %}
   </form>
   ```

3. **Vérifier JavaScript** :
   - Vérifier que script.js est chargé
   - Vérifier que `.needs-validation` a la classe `was-validated` après submit

4. **Tester la validation Python** :
   ```python
   if form.is_valid():
       form.save()
   else:
       print(form.errors)  # Pour déboguer
   ```

---

### 5. **Le layout n'est pas responsive**

#### ❌ Problème
La page s'affiche mal sur mobile, texte sort du conteneur, etc.

#### ✅ Solutions

1. **Vérifier la viewport meta tag** :
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   ```

2. **Vérifier les classes Bootstrap** :
   ```html
   <!-- ✅ Correct pour responsive -->
   <div class="row">
       <div class="col-12 col-md-6 col-lg-4">
           Contenu
       </div>
   </div>
   
   <!-- ❌ Incorrect (fixe) -->
   <div style="width: 500px">
       Contenu
   </div>
   ```

3. **Tester sur mobile** :
   - F12 → Toggle device toolbar
   - Tester sur différentes résolutions
   - iPhone 12, iPad, Desktop, etc.

4. **Vérifier les images** :
   ```html
   <!-- ✅ Correct -->
   <img src="..." class="img-fluid">
   
   <!-- ❌ Incorrect (trop grand) -->
   <img src="..." style="width: 1920px">
   ```

---

### 6. **Les animations ne fonctionnent pas**

#### ❌ Problème
Les animations CSS ne jouent pas, les transitions sont saccadées, etc.

#### ✅ Solutions

1. **Vérifier CSS animations dans style.css** :
   ```css
   @keyframes fadeIn {
       from { opacity: 0; }
       to { opacity: 1; }
   }
   
   .dynamic-text {
       animation: fadeIn 2s ease-in-out;
   }
   ```

2. **Vérifier performance** :
   - Trop d'animations = ralentissement
   - Limiter à 2-3 animations visibles en même temps
   - Utiliser `will-change` pour l'optimisation

3. **Vérifier JavaScript** :
   - F12 → Console pour erreurs
   - Vérifier que script.js est chargé
   - Tester les IntersectionObserver

4. **Alternative : Désactiver animations** :
   ```css
   @media (prefers-reduced-motion: reduce) {
       * {
           animation: none !important;
           transition: none !important;
       }
   }
   ```

---

### 7. **Les boutons ne s'affichent pas correctement**

#### ❌ Problème
Boutons manquants, mal alignés, couleurs incorrectes, texte invisible.

#### ✅ Solutions

1. **Vérifier les classes Bootstrap** :
   ```html
   <!-- ✅ Correct -->
   <button class="btn btn-primary">Cliquer</button>
   
   <!-- ❌ Incorrect -->
   <button class="button">Cliquer</button>
   <button style="background: blue;">Cliquer</button>
   ```

2. **Vérifier les couleurs** :
   ```css
   .btn-primary {
       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
       border: none;
       color: white;
   }
   ```

3. **Vérifier la taille** :
   ```html
   <!-- Tailles disponibles -->
   <button class="btn btn-sm">Petit</button>
   <button class="btn">Normal</button>
   <button class="btn btn-lg">Grand</button>
   ```

4. **Vérifier l'état disabled** :
   ```html
   <button class="btn btn-primary" disabled>
       Désactivé
   </button>
   ```

---

### 8. **Les tables s'affichent mal**

#### ❌ Problème
Tableau non responsive, texte sort de la cellule, colonnes mal alignées.

#### ✅ Solutions

1. **Wrapping responsive** :
   ```html
   <!-- ✅ Correct -->
   <div class="table-responsive">
       <table class="table">
           ...
       </table>
   </div>
   
   <!-- ❌ Incorrect -->
   <table class="table" style="width: 3000px">
   ```

2. **Vérifier les styles table** :
   ```css
   .table {
       margin-bottom: 1rem;
   }
   .table th,
   .table td {
       padding: 0.75rem;
       vertical-align: middle;
   }
   ```

3. **Colspan et rowspan** :
   ```html
   <!-- Correct pour colonnes multiples -->
   <th colspan="3">Actions</th>
   ```

4. **Tester sur mobile** :
   ```bash
   F12 → Toggle device toolbar → Mobile
   ```

---

### 9. **Le footer disparaît ou chevauche le contenu**

#### ❌ Problème
Footer en haut de la page ou caché sous le contenu.

#### ✅ Solutions

1. **Vérifier l'ordre des éléments dans base.html** :
   ```html
   <nav>...</nav>          <!-- Navbar -->
   <section>...</section>  <!-- Hero -->
   <main>...</main>        <!-- Contenu -->
   <footer>...</footer>    <!-- Footer -->
   ```

2. **Vérifier le CSS du footer** :
   ```css
   .footer {
       background: #343a40;
       color: white;
       padding: 20px 0;
       margin-top: auto;
       width: 100%;
   }
   ```

3. **Layout Flexbox** :
   ```css
   body {
       display: flex;
       flex-direction: column;
       min-height: 100vh;
   }
   main {
       flex: 1;
   }
   ```

4. **Position fixed** :
   ```css
   .navbar {
       position: fixed;
       top: 0;
       width: 100%;
       z-index: 1000;
   }
   main {
       margin-top: 70px; /* Hauteur navbar */
   }
   ```

---

### 10. **Les couleurs ne correspondent pas au design**

#### ❌ Problème
Couleurs différentes du design, gradient ne s'affiche pas, couleurs pales.

#### ✅ Solutions

1. **Vérifier la palette de couleurs** :
   ```css
   /* Couleurs définies */
   Primaire: #667eea (Violet bleu)
   Secondaire: #764ba2 (Violet)
   Texte: #2c3e50 (Bleu foncé)
   ```

2. **Vérifier les gradients** :
   ```css
   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   /* Pas de background-color simple */
   ```

3. **Vérifier l'opacité (rgba)** :
   ```css
   background: rgba(255, 255, 255, 0.95); /* 95% opaque */
   background: rgba(102, 126, 234, 0.3);  /* 30% opaque */
   ```

4. **Utiliser les bonnes classes** :
   ```html
   <!-- ✅ Correct -->
   <div class="bg-primary">Primary</div>
   <div class="text-danger">Danger</div>
   
   <!-- ❌ Incorrect -->
   <div class="bg-blue">Blue</div>
   ```

---

### 11. **Erreur 404 sur les fichiers statiques**

#### ❌ Problème
Console affiche 404 pour CSS/JS/images, style missing.

#### ✅ Solutions

1. **Vérifier les chemins** :
   ```
   ✅ Correct : static/css/style.css
   ❌ Incorrect : static/styles/style.css
   ❌ Incorrect : css/style.css (sans static/)
   ```

2. **Vérifier la structure des dossiers** :
   ```
   project/
   ├── static/
   │   ├── css/
   │   │   ├── style.css
   │   │   └── theme.css
   │   ├── js/
   │   │   └── script.js
   │   └── images/
   └── templates/
   ```

3. **Vérifier base.html** :
   ```html
   {% load static %}
   <link rel="stylesheet" href="{% static 'css/style.css' %}">
   ```

4. **Actualiser les statiques** :
   ```bash
   python manage.py collectstatic --clear
   python manage.py runserver
   ```

---

### 12. **Performance lente, page slow to load**

#### ❌ Problème
Temps de chargement long, animations saccadées, CPU/RAM élevée.

#### ✅ Solutions

1. **Minifier CSS/JS** :
   ```bash
   # Utiliser des outils de minification
   - cssnano
   - uglify-js
   - django-compressor
   ```

2. **Optimiser les images** :
   ```bash
   # Compresser les images
   - TinyPNG
   - ImageOptim
   - Squoosh
   ```

3. **Réduire les animations** :
   ```css
   /* Limit animations */
   /* Disable on slower devices */
   @media (prefers-reduced-motion: reduce) {
       * {
           animation: none !important;
       }
   }
   ```

4. **Utiliser CDN** :
   ```html
   <!-- Oui (CDN) -->
   <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
   
   <!-- Alternativement (local) -->
   <link href="{% static 'bootstrap/css/bootstrap.min.css' %}">
   ```

5. **Lazy loading images** :
   ```html
   <img src="..." loading="lazy">
   ```

---

## 📋 Checklist de Débogage

Avant de chercher une solution :

- [ ] Actualiser la page (F5)
- [ ] Hard refresh (Ctrl + Shift + R)
- [ ] Vider le cache du navigateur
- [ ] Vérifier la console (F12)
- [ ] Vérifier Network (F12 → Network)
- [ ] Vérifier les logs Django
- [ ] Exécuter `collectstatic`
- [ ] Redémarrer le serveur Django
- [ ] Tester sur un autre navigateur
- [ ] Tester en mode incognito

---

## 🔗 Ressources Utiles

1. **Bootstrap Documentation** : https://getbootstrap.com/docs/5.3/
2. **Font Awesome Icons** : https://fontawesome.com/
3. **MDN Web Docs** : https://developer.mozilla.org/
4. **Django Documentation** : https://docs.djangoproject.com/
5. **Can I Use** : https://caniuse.com/ (compatibilité navigateurs)

---

## 💬 Questions Fréquentes

### Q: Comment changer la couleur principale ?
**R:** Modifiez `#667eea` dans `style.css` et `theme.css`

### Q: Comment ajouter une nouvelle police ?
**R:** Ajoutez dans base.html :
```html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap">
<style> body { font-family: 'Poppins', sans-serif; } </style>
```

### Q: Comment désactiver les animations ?
**R:** Commentez les `@keyframes` dans style.css

### Q: Comment utiliser des images locales au lieu de placeholders ?
**R:** Mettez les images dans `static/images/` et utilisez :
```html
<img src="{% static 'images/mon-image.jpg' %}">
```

### Q: Comment ajouter une nouvelle page stylisée ?
**R:** Créez un template qui étend base.html et utilisez les classes Bootstrap

---

## 📞 Support Final

Si vous avez toujours un problème :

1. ✅ Consulter ce document
2. ✅ Vérifier STYLISATION_GUIDE.md
3. ✅ Examiner les fichiers CSS
4. ✅ Tester dans la console (F12)
5. ✅ Consulter la documentation officielle

**Bonne chance !** 🚀
