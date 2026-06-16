from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

class NotificationAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(email="zeinab@test.com", password="password123", name="Zeinab", phone_number='+201122334455')
        self.user2 = User.objects.create_user(email="yasmine@test.com", password="password123", name="Yasmine", phone_number='+201122334466')

        self.notif1 = Notification.objects.create(
            user=self.user1,
            message="Your booking is confirmed!",
            notification_type=Notification.NOTIFICATION_TYPES.BOOKING_CONFIRMED,
            is_read=False
        )
        self.notif2 = Notification.objects.create(
            user=self.user1,
            message="Event Reminder!",
            notification_type=Notification.NOTIFICATION_TYPES.EVENT_REMINDER,
            is_read=True
        )
        self.notif_yasmine = Notification.objects.create(
            user=self.user2,
            message="Yasmine's notification",
            notification_type=Notification.NOTIFICATION_TYPES.NEW_BOOKING
        )
        self.list_url = reverse('notifications-list') 
        self.detail_url = lambda pk: reverse('notifications-detail', kwargs={'pk': pk})
        self.read_url = lambda pk: reverse('notifications-read', kwargs={'pk': pk})
        self.read_all_url = reverse('notifications-read-all')


    def test_unauthenticated_user_cannot_access(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_see_their_own_notifications(self):
        self.client.force_authenticate(user=self.user1) 
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2) 

    def test_filter_by_is_read(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url, {'is_read': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.notif1.id)

    def test_global_patch_is_disallowed(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(self.detail_url(self.notif1.id), {"message": "Hacked message"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_mark_single_notification_as_read(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(self.read_url(self.notif1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notif1.refresh_from_db() 
        self.assertTrue(self.notif1.is_read)

    def test_mark_all_notifications_as_read(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(self.read_all_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(user=self.user1, is_read=False).count(), 0)
        self.notif_yasmine.refresh_from_db()
        self.assertFalse(self.notif_yasmine.is_read)

    def test_delete_notification(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url(self.notif1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(id=self.notif1.id).exists())