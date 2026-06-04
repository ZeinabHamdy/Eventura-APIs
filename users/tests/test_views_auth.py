from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

class AuthViewSetIntegrationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Zeinab',
            email='Zeinab@eventura.com',
            phone_number='+201122334455',
            password='Zeinab1234'
        )
        
    """ happy paths """
    def test_register_user_successfully(self):
        data = {
            'name': 'new user',
            'email': 'newuser@eventura.com',
            'phone_number': '+201122334466',
            'password': 'newuser1234',
            'password2': 'newuser1234'
        }
        response = self.client.post('/api/auth/register/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Account created successfully.') # type: ignore
        self.assertTrue(User.objects.filter(email='newuser@eventura.com').exists())

    def test_logout_user_successfully(self):
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh": str(refresh)}
        self.client.force_authenticate(user=self.user) # type: ignore
        response = self.client.post('/api/auth/logout/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_successfully(self):
        data = {
            "email": "Zeinab@eventura.com",
            "password": "Zeinab1234"
        }
        response = self.client.post('/api/auth/login/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data) # type: ignore
        self.assertIn('refresh', response.data) # type: ignore

    def test_token_refresh_successfully(self):
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh": str(refresh)}
        response = self.client.post('/api/auth/token/refresh/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data) # type: ignore

    """ unhappy paths """
    def test_register_with_existing_email_fails(self):
        data = {
            'name': 'Another Zeinab',
            'email': 'Zeinab@eventura.com', 
            'phone_number': '+201122334499',
            'password': 'password123',
            'password2': 'password123'
        }
        response = self.client.post('/api/auth/register/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_mismatch_password_fails(self):
        data = {
            'name': 'Another Zeinab',
            'email': 'Zeinab2@eventura.com', 
            'phone_number': '+201122334499',
            'password': 'password123456',
            'password2': 'password123'
        }
        response = self.client.post('/api/auth/register/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_invalid_token_fails(self):
        data = {"refresh": "fake_token"}
        self.client.force_authenticate(user=self.user) # type: ignore
        response = self.client.post('/api/auth/logout/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid token.') # type: ignore

    def test_login_with_wrong_password_fails(self):
        data = {
            "email": "Zeinab@eventura.com",
            "password": "wrong_password_123" 
        }
        response = self.client.post('/api/auth/login/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_non_existent_email_fails(self):
        data = {
            "email": "not_found_user@eventura.com",
            "password": "Zeinab1234"
        }
        response = self.client.post('/api/auth/login/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_with_invalid_token_fails(self):
        data = {"refresh": "completely_invalid_refresh_token"}
        response = self.client.post('/api/auth/token/refresh/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_inactive_user_fails(self):
        self.user.is_active = False
        self.user.save()
        data = {
            "email": "Zeinab@eventura.com",
            "password": "Zeinab1234"
        }
        response = self.client.post('/api/auth/login/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)