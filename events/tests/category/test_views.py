from rest_framework.test import APITestCase
from rest_framework import status


from users.models import User
from events.models.category import Category

class CategoryViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='user',
            email='user@eventura.com',
            phone_number='+201122334455',
            password='User1234'
        )
        self.admin_user = User.objects.create_superuser(
            name='admin user',
            email='admin_user@eventura.com',
            phone_number='+201122334466',
            password='admin_user1234'
        )
        self.category = Category.objects.create(name="Tech")

    def test_authenticated_user_can_list_categories(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_list_categories(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_user_can_create_category(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/categories/', {"name": "Business"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_normal_user_cannot_create_category(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/categories/', {"name": "Business"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_filter_by_name(self):
        self.client.force_authenticate(user=self.user)
        Category.objects.create(name="Health")
        response = self.client.get('/api/categories/', {'search': 'Hea'})
        self.assertEqual(len(response.data['results']), 1) 
        self.assertEqual(response.data['results'][0]['name'], "Health")  

    def test_admin_user_can_delete_category(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/categories/{self.category.id}/') 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists()) 

    def test_normal_user_cannot_delete_category(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/categories/{self.category.id}/') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Category.objects.filter(id=self.category.id).exists()) 