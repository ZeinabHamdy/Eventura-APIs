from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError as DRFValidationError


from users.models import User
from events.models.category import Category
from events.models.event import Event
from events.models.ticket_type import TicketType
from events.serializers.ticket_type_serializer import(
    TicketTypeCreateSerializer,
    TicketTypeReadSerializer,
    TicketTypeUpdateSerializer,
    TicketTypeUpdateWithBookingSerializer,
)



class TicketTypeSerializerTestCase(TestCase):
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
    
    def test_read_serializer_read_all_fields(self):
        ticket = TicketType.objects.create(
            event = self.published_event,
            name='vip',
            price=200,
            total_seats=50,
            available_seats=50
        )
        serializer = TicketTypeReadSerializer(instance=ticket)
        expected_fields = {'id', 'name', 'price', 'total_seats', 'available_seats', 'event', 'created_at', 'updated_at'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_create_serializer_made_available_seats_read_only(self):
        data = {
            "name": "vip",
            "price": "200",
            "total_seats": 50,
            "available_seats": 10,
            "event": self.published_event.pk
        }
        serializer = TicketTypeCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('available_seats', serializer.validated_data)

    def test_update_serializer_restricts_available_seats(self):
        ticket = TicketType.objects.create(
            event=self.published_event,
            name="regular",
            price=100.00,
            total_seats=50,
            available_seats=50
        )
        data = {
            "name": "vip",
            "price": "200.00",
            "total_seats": 50,
            "available_seats": 10
        }
        serializer = TicketTypeUpdateSerializer(instance=ticket, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('available_seats', serializer.validated_data)

    def test_update_with_booking_serializer_blocks_any_field_except_total_seats(self):
        ticket = TicketType.objects.create(
            event=self.published_event,
            name="regular",
            price=100.00,
            total_seats=50,
            available_seats=50
        )
        invalid_data = {
            "total_seats": 70,
            "price": "150.00",
            "name": "vip"
        }
        serializer = TicketTypeUpdateWithBookingSerializer(instance=ticket, data=invalid_data, partial=True)
        with self.assertRaises(DRFValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Only total_seats can be updated", str(context.exception))