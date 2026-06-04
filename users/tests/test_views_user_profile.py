from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User


class UserViewSetIntegrationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='User',
            email='User@eventura.com',
            phone_number='+201122334455',
            password='OldPassword1234'
        )
        self.other_user = User.objects.create_user(
            name='Other User',
            email='Other@eventura.com',
            phone_number='+201122334466',
            password='OtherPassword1234'
        )

    """ happy paths """
    def test_get_own_profile_successfully(self):
        self.client.force_authenticate(user=self.user) # type: ignore
        response = self.client.get('/api/users/me/') 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email) # type: ignore
        self.assertEqual(response.data['name'], self.user.name) # type: ignore

    def test_update_own_profile_successfully(self):
        self.client.force_authenticate(user=self.user) # type: ignore
        data = {
            'name': 'User Updated',
            'phone_number': '+201199999999',
            'email': 'newemail@eventura.com'
        }
        response = self.client.patch('/api/users/me/', data=data) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'User Updated')
        self.assertEqual(self.user.phone_number, '+201199999999')
        self.assertEqual(self.user.email, 'user@eventura.com')

    def test_change_password_successfully(self):
        self.client.force_authenticate(user=self.user) # type: ignore
        data = {
            'old_password': 'OldPassword1234',
            'new_password': 'NewPassword1234',
            'new_password2': 'NewPassword1234'
        }
        response = self.client.post('/api/users/change-password/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword1234'))

    def test_delete_account_soft_deletes_successfully(self):
        self.client.force_authenticate(user=self.user) # type: ignore
        response = self.client.delete('/api/users/delete-account/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


    """ unhappy paths """
    def test_get_profile_unauthenticated_fails(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_with_wrong_old_password_fails(self):
        self.client.force_authenticate(user=self.user) # type: ignore
        data = {
            'old_password': 'wrong_old_password',
            'new_password': 'NewSecurePassword1234',
            'new_password2': 'NewSecurePassword1234'
        }
        response = self.client.post('/api/users/change-password/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_with_mismatch_new_passwords_fails(self):
        self.client.force_authenticate(user=self.user) #type: ignore
        data = {
            'old_password': 'OldPassword1234',
            'new_password': 'NewSecurePassword1234',
            'new_password2': 'different_new_password' 
        }
        response = self.client.post('/api/users/change-password/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)