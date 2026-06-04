from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from events.models.category import Category
from events.models.event import Event


class EventViewSetTestCase(APITestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            email="organizer@eventura.com", password="Password1234", phone_number="+201122334455", name="Organizer User"
        )
        self.other_user = User.objects.create_user(
            email="other@eventura.com", password="Password1234", phone_number="+201222334466", name="Other User"
        ) 
        self.category = Category.objects.create(name="Tech")
        self.now = timezone.now()
        self.list_url = reverse('event-list')  
        self.future_start = self.now + timedelta(days=2)
        self.future_end = self.now + timedelta(days=3)

    def _create_event(self, name="Test Event", status="drafted", organizer=None):
        return Event.objects.create(
            name=name,
            description="Event Description",
            location_type="online",
            location_link="http://127.0.0.1:8000/admin/",
            start_date=self.future_start,
            end_date=self.future_end,
            status=status,
            category=self.category,
            organizer=organizer
        )

    def test_list_events_shows_published_and_cancelled_to_everyone(self):
        self._create_event(name="Published Event", status="published", organizer=self.organizer)
        self._create_event(name="Cancelled Event", status="cancelled", organizer=self.organizer)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2)

    def test_list_events_hides_other_organizers_drafts(self):
        self._create_event(name="My Draft", status="drafted", organizer=self.organizer)
        self._create_event(name="Other Draft", status="drafted", organizer=self.other_user)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_url)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Other Draft")

    def test_update_drafted_event_by_organizer_success(self):
        event = self._create_event(name="Draft Event", status="drafted", organizer=self.organizer)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        self.client.force_authenticate(user=self.organizer)
        data = {"name": "Updated Name", "description": "New description"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.name, "Updated Name")

    def test_update_published_event_by_organizer_success(self):
        event = self._create_event(name="Draft Event", status="published", organizer=self.organizer)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        self.client.force_authenticate(user=self.organizer)
        data = {"description": "New description"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.description, "New description")

    def test_update_published_event_only_allows_description(self):
        event = self._create_event(name="Published Event", status="published", organizer=self.organizer)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        self.client.force_authenticate(user=self.organizer)
        data = {"name": "Hack the Name", "description": "New description"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Only description can be updated', str(response.data))

    def test_update_drafted_event_by_non_organizer_raises_not_found(self):
        # as get_queryset in view not allowed other prople to show drafted events of others
        event = self._create_event(name="Draft Event", status="drafted", organizer=self.organizer)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(url, {"name": "updated name"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_published_event_by_non_organizer_raises_forbidden(self):
        event = self._create_event(name="Published Event", status="published", organizer=self.organizer)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(url, {"description": "updated name"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_cancelled_event_raises_validation_error(self):
        event = self._create_event(name="Cancelled Event", status="cancelled", organizer=self.organizer)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        self.client.force_authenticate(user=self.organizer)
        response = self.client.patch(url, {"description": "updated desc"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot update a cancelled event.', response.data[0])

    def test_update_status_endpoint_success(self):
        event = self._create_event(name="Draft Event", status="drafted", organizer=self.organizer)
        url = reverse('event-update-status', kwargs={'pk': event.pk})
        self.client.force_authenticate(user=self.organizer)
        response = self.client.patch(url, {"status": "published"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.status, "published")

    def test_organizer_events_endpoint_returns_only_published(self):
        self._create_event(name="Published event", status="published", organizer=self.organizer)
        self._create_event(name="Draft event", status="drafted", organizer=self.organizer)
        url = reverse('event-organizer-events', kwargs={'organizer_pk': self.organizer.pk})
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Published event")

    def test_delete_event_without_bookings_success(self):
        event = self._create_event(name="Clean Event", status="published", organizer=self.organizer)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        self.client.force_authenticate(user=self.organizer)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(pk=event.pk).exists())

    def test_delete_event_with_bookings_raises_error(self):
        event = self._create_event(name="Event with bookings", status="published", organizer=self.organizer)
        url = reverse('event-detail', kwargs={'pk': event.pk})
        from unittest.mock import patch
        with patch('django.db.models.query.QuerySet.exists', return_value=True):
            self.client.force_authenticate(user=self.organizer)
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Cannot delete an event that has bookings.', response.data[0])
            self.assertTrue(Event.objects.filter(pk=event.pk).exists())

    def test_list_events_by_unauthenticated_user_raises_unauthorized(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_organizer_events_with_invalid_pk_raises_not_found(self):
        url = reverse('event-organizer-events', kwargs={'organizer_pk': 99999})
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Organizer not found.')

    def test_create_event_by_authenticated_user_success(self):
        self.client.force_authenticate(user=self.organizer)
        data = {
            "name": "new event",
            "description": "Let's learn unit testing",
            "location_type": "online",
            "location_link": "http://127.0.0.1:8000/admin/",
            "start_date": str(self.future_start.date()),
            "end_date": str(self.future_end.date()),
            "status": "drafted",
            "category": self.category.pk
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_event = Event.objects.get(name="new event")
        self.assertEqual(new_event.organizer, self.organizer)

    def test_create_event_with_invalid_logic_raises_validation_error(self):
        self.client.force_authenticate(user=self.organizer)
        data = {
            "name": "Broken Event",
            "description": "Testing validators via view",
            "location_type": "online",
            "location_link": "http://127.0.0.1:8000/admin/",
            "start_date": str(self.now + timedelta(days=5)), 
            "end_date": str(self.now + timedelta(days=1)), 
            "status": "drafted",
            "category": self.category.pk
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)