from datetime import timedelta
from django.utils import timezone

from django.test import TestCase
from django.core.exceptions import ValidationError



from users.models import User
from events.models.category import Category
from events.models.event import Event

from events.validators.ticket_type_validators import(
    validate_event_published_when_create_ticket_type,
    validate_price,
    validate_seats,
)


class TicketTypeValidatorsTestCase(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            email="organizer@eventura.com",
            password="Password1234",
            phone_number="+201122334455",
            name="Organizer"
        )
        self.category = Category.objects.create(name="Tech")
        self.now = timezone.now()

    def test_validate_seats_available_more_than_total_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            validate_seats(total_seats=50, available_seats=60)
        self.assertEqual(context.exception.messages[0], "Available seats can't be more than total seats")
    
    def test_validate_seats_total_less_than_one_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            validate_seats(total_seats=0, available_seats=0)
        self.assertEqual(context.exception.messages[0], "Total seats must be at least 1")

    def test_validate_make_ticket_type_for_drafted_event_raises_error(self):
        draft_event = Event.objects.create(
            name="Drafted Event",
            description="Desc",
            location_type="online",
            location_link="https://www.eventura.com",
            start_date=self.now + timedelta(days=2),
            end_date=self.now + timedelta(days=3),
            status="drafted",
            category=self.category,
            organizer=self.organizer
        )
        with self.assertRaises(ValidationError) as context:
            validate_event_published_when_create_ticket_type(draft_event)
        self.assertEqual(context.exception.messages[0], "Cannot create ticket type for unpublished event")

    def test_validate_free_ticket_with_positive_price_raise_fail(self):
        with self.assertRaises(ValidationError) as context:
            validate_price(name="free", price=10.00)
        self.assertEqual(context.exception.messages[0], "Free ticket price must be 0")

    def test_validate_price_not_free_with_zero_price_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            validate_price(name="regular", price=0.00)
        self.assertEqual(context.exception.messages[0], "Price must be positive")