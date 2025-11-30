# 💡 Snippets et Exemples Réutilisables

Ce fichier contient des exemples de code que vous pouvez copier-coller directement dans vos templates.

---

## 🎯 Composants Courants

### 1. Card Simple
```django
<div class="card shadow-lg">
    <div class="card-header bg-primary text-white">
        <h3>Titre</h3>
    </div>
    <div class="card-body">
        <p>Contenu ici</p>
    </div>
    <div class="card-footer">
        <a href="#" class="btn btn-primary">Action</a>
    </div>
</div>
```

### 2. Card avec Multiple Sections
```django
<div class="card shadow-lg">
    <div class="card-header bg-primary text-white">
        <h3>Informations</h3>
    </div>
    <div class="card-body">
        <div class="row mb-3">
            <div class="col-md-4">
                <strong>Nom :</strong>
            </div>
            <div class="col-md-8">
                <span class="text-muted">{{ object.name }}</span>
            </div>
        </div>
        
        <div class="row mb-3">
            <div class="col-md-4">
                <strong>Date :</strong>
            </div>
            <div class="col-md-8">
                <span class="text-muted">{{ object.date|date:"d F Y" }}</span>
            </div>
        </div>
    </div>
</div>
```

### 3. Tableau Responsive
```django
<div class="table-responsive">
    <table class="table table-hover table-striped">
        <thead class="table-light">
            <tr>
                <th><i class="fas fa-user"></i> Nom</th>
                <th><i class="fas fa-envelope"></i> Email</th>
                <th class="text-center"><i class="fas fa-cog"></i> Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ item.name }}</td>
                <td>{{ item.email }}</td>
                <td class="text-center">
                    <a href="#" class="btn btn-sm btn-info">
                        <i class="fas fa-eye"></i> Voir
                    </a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="3" class="text-center text-muted">
                    <i class="fas fa-inbox"></i> Aucun élément
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### 4. Formulaire Personnalisé
```django
<div class="card shadow-lg">
    <div class="card-header bg-primary text-white">
        <h2>Formulaire</h2>
    </div>
    <div class="card-body">
        <form method="post" class="needs-validation" novalidate>
            {% csrf_token %}
            
            {% for field in form %}
            <div class="mb-3">
                <label for="{{ field.id_for_label }}" class="form-label">
                    {{ field.label }}
                    {% if field.field.required %}
                    <span class="text-danger">*</span>
                    {% endif %}
                </label>
                
                {% if field.widget.input_type == "textarea" %}
                    <textarea 
                        class="form-control {% if field.errors %}is-invalid{% endif %}"
                        id="{{ field.id_for_label }}"
                        name="{{ field.name }}"
                        rows="4">{{ field.value|default:"" }}</textarea>
                {% else %}
                    <input 
                        type="{{ field.widget.input_type }}"
                        class="form-control {% if field.errors %}is-invalid{% endif %}"
                        id="{{ field.id_for_label }}"
                        name="{{ field.name }}"
                        value="{{ field.value|default:"" }}">
                {% endif %}
                
                {% if field.help_text %}
                <small class="form-text text-muted">{{ field.help_text|safe }}</small>
                {% endif %}
                
                {% if field.errors %}
                <div class="invalid-feedback d-block">
                    {% for error in field.errors %}
                    {{ error }}<br>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
            
            <button type="submit" class="btn btn-primary btn-lg">
                <i class="fas fa-save"></i> Enregistrer
            </button>
        </form>
    </div>
</div>
```

### 5. Alerte d'Information
```django
<div class="alert alert-info alert-dismissible fade show" role="alert">
    <i class="fas fa-info-circle"></i> <strong>Information !</strong>
    Ceci est un message d'information.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### 6. Alerte d'Avertissement
```django
<div class="alert alert-warning alert-dismissible fade show" role="alert">
    <i class="fas fa-exclamation-triangle"></i> <strong>Attention !</strong>
    Ceci est un message d'avertissement.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### 7. Alerte d'Erreur
```django
<div class="alert alert-danger alert-dismissible fade show" role="alert">
    <i class="fas fa-times-circle"></i> <strong>Erreur !</strong>
    Ceci est un message d'erreur.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### 8. Alerte de Succès
```django
<div class="alert alert-success alert-dismissible fade show" role="alert">
    <i class="fas fa-check-circle"></i> <strong>Succès !</strong>
    L'opération a réussi.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

### 9. Confirmation Modal
```django
<div class="modal fade" id="confirmModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title">Confirmation</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                Êtes-vous sûr de vouloir continuer ?
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                    Annuler
                </button>
                <button type="button" class="btn btn-danger">
                    Confirmer
                </button>
            </div>
        </div>
    </div>
</div>
```

### 10. Section Vide
```django
<div class="empty-state text-center py-5">
    <div class="empty-state-icon">
        <i class="fas fa-inbox"></i>
    </div>
    <h3 class="empty-state-title">Aucune donnée</h3>
    <p class="empty-state-description">
        Il n'y a pas d'éléments à afficher pour le moment.
    </p>
    <a href="#" class="btn btn-primary">
        <i class="fas fa-plus"></i> Créer un élément
    </a>
</div>
```

---

## 📊 Layouts Courants

### 1. Layout Sidebar + Contenu
```django
<div class="container my-5">
    <div class="row">
        <div class="col-md-3">
            <!-- Sidebar -->
            <div class="card sticky-top">
                <div class="card-body">
                    <ul class="list-unstyled">
                        <li><a href="#">Lien 1</a></li>
                        <li><a href="#">Lien 2</a></li>
                        <li><a href="#">Lien 3</a></li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="col-md-9">
            <!-- Contenu principal -->
            <div class="card">
                <div class="card-body">
                    Contenu ici
                </div>
            </div>
        </div>
    </div>
</div>
```

### 2. Layout 3 Colonnes
```django
<div class="container my-5">
    <div class="row g-4">
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-body">Colonne 1</div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-body">Colonne 2</div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card">
                <div class="card-body">Colonne 3</div>
            </div>
        </div>
    </div>
</div>
```

### 3. Layout Hero + Contenu
```django
<section class="hero-section">
    <div class="container text-center text-white">
        <h1 class="display-4 fw-bold">Titre Principal</h1>
        <p class="lead">Sous-titre descriptif</p>
        <a href="#" class="btn btn-primary btn-lg">Commencer</a>
    </div>
</section>

<main class="container my-5">
    <!-- Contenu ici -->
</main>
```

---

## 🔘 Boutons Spécialisés

### 1. Groupe de Boutons
```django
<div class="btn-group" role="group">
    <button type="button" class="btn btn-primary">Gauche</button>
    <button type="button" class="btn btn-primary">Centre</button>
    <button type="button" class="btn btn-primary">Droite</button>
</div>
```

### 2. Bouton avec Dropdown
```django
<div class="dropdown">
    <button class="btn btn-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
        Actions
    </button>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="#">Éditer</a></li>
        <li><a class="dropdown-item" href="#">Supprimer</a></li>
        <li><hr class="dropdown-divider"></li>
        <li><a class="dropdown-item" href="#">Exporter</a></li>
    </ul>
</div>
```

### 3. Bouton Toggle
```django
<button type="button" class="btn btn-primary" data-bs-toggle="button" autocomplete="off">
    Actif/Inactif
</button>
```

### 4. Bouton avec Loading
```django
<button type="submit" class="btn btn-primary" id="submitBtn">
    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" style="display: none;"></span>
    <span class="btn-text">Soumettre</span>
</button>

<script>
const form = document.querySelector('form');
form.addEventListener('submit', function() {
    const btn = document.getElementById('submitBtn');
    btn.querySelector('.spinner-border').style.display = 'inline-block';
    btn.querySelector('.btn-text').textContent = 'Traitement...';
    btn.disabled = true;
});
</script>
```

---

## 🏷️ Badges et Labels

### 1. Badges Simples
```django
<span class="badge bg-primary">Primary</span>
<span class="badge bg-secondary">Secondary</span>
<span class="badge bg-success">Success</span>
<span class="badge bg-danger">Danger</span>
<span class="badge bg-warning text-dark">Warning</span>
<span class="badge bg-info">Info</span>
```

### 2. Badges avec Statuts
```django
{% if object.status == 'pending' %}
    <span class="badge bg-warning">En attente</span>
{% elif object.status == 'approved' %}
    <span class="badge bg-success">Approuvé</span>
{% elif object.status == 'rejected' %}
    <span class="badge bg-danger">Rejeté</span>
{% endif %}
```

### 3. Étiquettes Personnalisées
```django
<span class="status-badge status-pending">
    <i class="fas fa-clock"></i> En attente
</span>

<span class="status-badge status-approved">
    <i class="fas fa-check"></i> Approuvé
</span>

<span class="status-badge status-rejected">
    <i class="fas fa-times"></i> Rejeté
</span>
```

---

## 📝 Barre de Recherche

### 1. Recherche Simple
```django
<div class="mb-3">
    <form method="get" class="input-group">
        <input 
            type="text" 
            class="form-control" 
            name="q" 
            placeholder="Rechercher..."
            value="{{ request.GET.q }}">
        <button class="btn btn-primary" type="submit">
            <i class="fas fa-search"></i>
        </button>
    </form>
</div>
```

### 2. Recherche Avancée
```django
<div class="card mb-3">
    <div class="card-body">
        <form method="get" class="row g-3">
            <div class="col-md-4">
                <input type="text" class="form-control" name="q" placeholder="Nom">
            </div>
            <div class="col-md-4">
                <select class="form-select" name="category">
                    <option>Tous les catégories</option>
                    {% for cat in categories %}
                    <option value="{{ cat.id }}">{{ cat.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-4">
                <button type="submit" class="btn btn-primary w-100">
                    <i class="fas fa-search"></i> Rechercher
                </button>
            </div>
        </form>
    </div>
</div>
```

---

## 📅 Pagination

### 1. Pagination Simple
```django
{% if is_paginated %}
<nav aria-label="Page navigation" class="mt-4">
    <ul class="pagination justify-content-center">
        {% if page_obj.has_previous %}
        <li class="page-item">
            <a class="page-link" href="?page=1">
                <i class="fas fa-chevron-left"></i> Première
            </a>
        </li>
        <li class="page-item">
            <a class="page-link" href="?page={{ page_obj.previous_page_number }}">
                Précédente
            </a>
        </li>
        {% endif %}
        
        {% for num in page_obj.paginator.page_range %}
            {% if page_obj.number == num %}
            <li class="page-item active">
                <span class="page-link">
                    {{ num }}
                    <span class="visually-hidden">(page actuelle)</span>
                </span>
            </li>
            {% else %}
            <li class="page-item">
                <a class="page-link" href="?page={{ num }}">{{ num }}</a>
            </li>
            {% endif %}
        {% endfor %}
        
        {% if page_obj.has_next %}
        <li class="page-item">
            <a class="page-link" href="?page={{ page_obj.next_page_number }}">
                Suivante
            </a>
        </li>
        <li class="page-item">
            <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">
                Dernière <i class="fas fa-chevron-right"></i>
            </a>
        </li>
        {% endif %}
    </ul>
</nav>
{% endif %}
```

---

## 🔒 Formulaires Sécurisés

### 1. Confirmation Avant Suppression
```django
<a href="{% url 'delete' object.pk %}" 
   class="btn btn-danger"
   onclick="return confirm('Êtes-vous sûr de vouloir supprimer ?');">
    <i class="fas fa-trash"></i> Supprimer
</a>
```

### 2. Formulaire avec CSRF
```django
<form method="post" action="{% url 'submit' %}">
    {% csrf_token %}
    
    <div class="mb-3">
        <label class="form-label">Texte</label>
        <input type="text" class="form-control" name="text" required>
    </div>
    
    <button type="submit" class="btn btn-primary">
        Soumettre
    </button>
</form>
```

### 3. Formulaire Multi-Étapes
```django
<div class="card">
    <div class="card-header">
        <ul class="nav nav-tabs card-header-tabs">
            <li class="nav-item">
                <a class="nav-link active" href="#step1" data-bs-toggle="tab">
                    Étape 1
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#step2" data-bs-toggle="tab">
                    Étape 2
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#step3" data-bs-toggle="tab">
                    Étape 3
                </a>
            </li>
        </ul>
    </div>
    <div class="card-body">
        <div class="tab-content">
            <div class="tab-pane fade show active" id="step1">
                Contenu étape 1
            </div>
            <div class="tab-pane fade" id="step2">
                Contenu étape 2
            </div>
            <div class="tab-pane fade" id="step3">
                Contenu étape 3
            </div>
        </div>
    </div>
</div>
```

---

## 💾 Sauvegarde Rapide

Copier-coller l'une de ces structures dans votre code pour commencer rapidement !

**Bonne codification !** ✨
