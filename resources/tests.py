from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Resource, Aid, Category, Club, Favorite


class FavoriteModelTest(TestCase):
    """Tests pour le modèle Favorite."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.category = Category.objects.create(name="Test Category")
        self.club = Club.objects.create(name="Test Club")
        self.resource = Resource.objects.create(
            title="Test Resource",
            description="Test Description",
            category=self.category,
            club=self.club,
            submitted_by=self.user,
            is_validated=True
        )
        self.aid = Aid.objects.create(
            title="Test Aid",
            description="Test Description",
            category=self.category,
            club=self.club,
            submitted_by=self.user,
            is_validated=True
        )
    
    def test_create_favorite_resource(self):
        """Test la création d'un favori pour une ressource."""
        favorite = Favorite.objects.create(
            user=self.user,
            resource=self.resource
        )
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.resource, self.resource)
        self.assertIsNone(favorite.aid)
        self.assertEqual(str(favorite), f"{self.user.username} - {self.resource.title}")
    
    def test_create_favorite_aid(self):
        """Test la création d'un favori pour une aide."""
        favorite = Favorite.objects.create(
            user=self.user,
            aid=self.aid
        )
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.aid, self.aid)
        self.assertIsNone(favorite.resource)
        self.assertEqual(str(favorite), f"{self.user.username} - {self.aid.title}")
    
    def test_prevent_duplicate_favorite_resource(self):
        """Test qu'on ne peut pas créer deux favoris identiques pour une ressource."""
        Favorite.objects.create(user=self.user, resource=self.resource)
        
        # Tentative de créer un doublon
        with self.assertRaises(Exception):  # unique_together lève une exception
            Favorite.objects.create(user=self.user, resource=self.resource)
    
    def test_prevent_duplicate_favorite_aid(self):
        """Test qu'on ne peut pas créer deux favoris identiques pour une aide."""
        Favorite.objects.create(user=self.user, aid=self.aid)
        
        # Tentative de créer un doublon
        with self.assertRaises(Exception):  # unique_together lève une exception
            Favorite.objects.create(user=self.user, aid=self.aid)
    
    def test_different_users_can_favorite_same_resource(self):
        """Test que différents utilisateurs peuvent favoriser la même ressource."""
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        
        favorite1 = Favorite.objects.create(user=self.user, resource=self.resource)
        favorite2 = Favorite.objects.create(user=user2, resource=self.resource)
        
        self.assertNotEqual(favorite1, favorite2)
        self.assertEqual(Favorite.objects.filter(resource=self.resource).count(), 2)


class FavoriteViewsTest(TestCase):
    """Tests pour les vues de favoris."""
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Test Category")
        self.club = Club.objects.create(name="Test Club")
        self.resource = Resource.objects.create(
            title="Test Resource",
            description="Test Description",
            category=self.category,
            club=self.club,
            submitted_by=self.user,
            is_validated=True
        )
        self.aid = Aid.objects.create(
            title="Test Aid",
            description="Test Description",
            category=self.category,
            club=self.club,
            submitted_by=self.user,
            is_validated=True
        )
    
    def test_toggle_favorite_resource_add(self):
        """Test l'ajout d'une ressource aux favoris."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('resources:resource_favorite', args=[self.resource.pk])
        
        # Ajouter aux favoris
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertTrue(Favorite.objects.filter(user=self.user, resource=self.resource).exists())
    
    def test_toggle_favorite_resource_remove(self):
        """Test le retrait d'une ressource des favoris."""
        self.client.login(username='testuser', password='testpass123')
        Favorite.objects.create(user=self.user, resource=self.resource)
        url = reverse('resources:resource_favorite', args=[self.resource.pk])
        
        # Retirer des favoris
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertFalse(Favorite.objects.filter(user=self.user, resource=self.resource).exists())
    
    def test_toggle_favorite_aid_add(self):
        """Test l'ajout d'une aide aux favoris."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('resources:aid_favorite', args=[self.aid.pk])
        
        # Ajouter aux favoris
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertTrue(Favorite.objects.filter(user=self.user, aid=self.aid).exists())
    
    def test_toggle_favorite_aid_remove(self):
        """Test le retrait d'une aide des favoris."""
        self.client.login(username='testuser', password='testpass123')
        Favorite.objects.create(user=self.user, aid=self.aid)
        url = reverse('resources:aid_favorite', args=[self.aid.pk])
        
        # Retirer des favoris
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertFalse(Favorite.objects.filter(user=self.user, aid=self.aid).exists())
    
    def test_favorites_list_requires_login(self):
        """Test que la liste des favoris nécessite une connexion."""
        url = reverse('resources:favorites_list')
        response = self.client.get(url)
        
        # Doit rediriger vers la page de connexion
        self.assertEqual(response.status_code, 302)
    
    def test_favorites_list_authenticated(self):
        """Test l'affichage de la liste des favoris pour un utilisateur connecté."""
        self.client.login(username='testuser', password='testpass123')
        Favorite.objects.create(user=self.user, resource=self.resource)
        Favorite.objects.create(user=self.user, aid=self.aid)
        
        url = reverse('resources:favorites_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mes favoris")
        self.assertEqual(len(response.context['favorites']), 2)
    
    def test_favorites_list_filter_by_type(self):
        """Test le filtre par type dans la liste des favoris."""
        self.client.login(username='testuser', password='testpass123')
        Favorite.objects.create(user=self.user, resource=self.resource)
        Favorite.objects.create(user=self.user, aid=self.aid)
        
        # Filtrer par ressources
        url = reverse('resources:favorites_list') + '?type=resources'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['favorites']), 1)
        self.assertIsNotNone(response.context['favorites'][0].resource)
        
        # Filtrer par aides
        url = reverse('resources:favorites_list') + '?type=aids'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['favorites']), 1)
        self.assertIsNotNone(response.context['favorites'][0].aid)
