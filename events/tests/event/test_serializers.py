from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from events.models.category import Category
from users.models import User
from events.models.event import Event
from events.serializers.event_serializer import (
    EventUpdatePublishedSerializer,
    EventUpdateStatusSerializer,
    EventListSerializer
)

class EventSerializersTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="organizer@eventura.com", password="Password123", phone_number="+201122334455", name="user")
        self.category = Category.objects.create(name="Tech")
        self.event = Event.objects.create(
            name="Django Workshop",
            description="Learn DRF",
            location_type="online",
            location_link="https://zoom/mettinglink/",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
            status="published",
            category=self.category,
            organizer=self.user
        )
    """ update published events (happy and unhappy) """
    def test_update_published_event_description_success(self):
        data = {"description": "Updated description for the workshop"}
        serializer = EventUpdatePublishedSerializer(instance=self.event, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['description'], data['description'])

    def test_update_published_event_with_invalid_fields_raises_error(self):
        data = {
            "description": "Updated description",
            "name": "Hackathon 2026",
            "location_type": "offline" 
        }
        serializer = EventUpdatePublishedSerializer(instance=self.event, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Only description can be updated', serializer.errors['non_field_errors'][0])
        self.assertIn('name', serializer.errors['non_field_errors'][0])
        self.assertIn('location_type', serializer.errors['non_field_errors'][0])

    """ in change status """
    def test_update_status_success(self):
        data = {"status": "cancelled"}
        serializer = EventUpdateStatusSerializer(instance=self.event, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['status'], data['status'])

    def test_update_status_with_invalid_fields_raises_error(self):
        data = {
            "status": "cancelled",
            "description": "updated description" 
        }
        serializer = EventUpdateStatusSerializer(instance=self.event, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Only status can be updated', serializer.errors['non_field_errors'][0])

    def test_event_list_serializer_returns_expected_fields(self):
        self.event.average_rating = 4.50
        self.event.review_count = 10
        serializer = EventListSerializer(instance=self.event)
        expected_fields = {'name', 'start_date', 'location_type', 'status', 'category', 'average_rating', 'review_count'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
        self.assertEqual(serializer.data['category'], "Tech")