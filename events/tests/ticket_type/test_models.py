from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError as DjangoValidationError


from users.models import User
from events.models.category import Category
from events.models.event import Event
from events.models.ticket_type import TicketType


class TicketTypeModelTestCase(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            email="organizer@eventura.com",
            password="Password1234",
            phone_number="+201122334455",
            name="Organizer"
        )
        self.category = Category.objects.create(name="Tech")
        self.now = timezone.now()
        self.published_event = Event.objects.create(
            name="Published Event",
            description="Desc",
            location_type="online",
            location_link="https://www.eventura.com",
            start_date=self.now + timedelta(days=2),
            end_date=self.now + timedelta(days=3),
            status="published",
            category=self.category,
            organizer=self.organizer
        )

    def test_unique_constraint_at_database_level(self):
        TicketType.objects.create(event=self.published_event, name="vip", price=500.00, total_seats=10, available_seats=10)
        with self.assertRaises(DjangoValidationError):
            TicketType.objects.create(event=self.published_event, name="vip", price=600.00, total_seats=5, available_seats=5)