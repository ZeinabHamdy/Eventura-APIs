from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from users.models import User
from events.models.category import Category
from events.models.event import Event
from events.models.ticket_type import TicketType
from bookings.models import Booking, WaitlistEntry


class BookingModelTestCase(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            email='organizer@eventura.com',
            password='Password1234',
            name='Organizer',
            phone_number='+201122334455'
        )
        self.user = User.objects.create_user(
            email='user@eventura.com',
            password='Password1234',
            name='User',
            phone_number='+201122334466'
        )
        self.category = Category.objects.create(name='Tech')
        self.event = Event.objects.create(
            name='Test Event',
            location_type='online',
            location_link='https://eventura.com',
            start_date=timezone.now() + timedelta(days=2),
            end_date=timezone.now() + timedelta(days=3),
            status='published',
            category=self.category,
            organizer=self.organizer
        )
        self.ticket_type = TicketType.objects.create(
            name='regular',
            price=100,
            total_seats=10,
            available_seats=10,
            event=self.event
        )

    def test_unique_constraint_prevents_double_confirmed_booking(self):
        Booking.objects.create(user=self.user, ticket_type=self.ticket_type)
        with self.assertRaises(ValidationError):
            Booking.objects.create(user=self.user, ticket_type=self.ticket_type)

    def test_unique_constraint_allows_new_booking_after_cancellation(self):
        booking = Booking.objects.create(user=self.user, ticket_type=self.ticket_type)
        booking.status = Booking.STATUS.CANCELLED
        booking.save()
        try:
            Booking.objects.create(user=self.user, ticket_type=self.ticket_type)
        except ValidationError:
            self.fail("Should allow new booking after cancellation!")

    def test_cannot_reactivate_cancelled_booking(self):
        booking = Booking.objects.create(user=self.user, ticket_type=self.ticket_type)
        booking.status = Booking.STATUS.CANCELLED
        booking.save()
        booking.status = Booking.STATUS.CONFIRMED
        with self.assertRaises(ValidationError):
            booking.save()


class WaitlistEntryModelTestCase(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            email='organizer@eventura.com',
            password='Password1234',
            name='Organizer',
            phone_number='+201122334455'
        )
        self.user = User.objects.create_user(
            email='user@eventura.com',
            password='Password1234',
            name='User',
            phone_number='+201122334466'
        )
        self.category = Category.objects.create(name='Tech')
        self.event = Event.objects.create(
            name='Test Event',
            location_type='online',
            location_link='https://eventura.com',
            start_date=timezone.now() + timedelta(days=2),
            end_date=timezone.now() + timedelta(days=3),
            status='published',
            category=self.category,
            organizer=self.organizer
        )
        self.ticket_type = TicketType.objects.create(
            name='regular',
            price=100,
            total_seats=10,
            available_seats=10,
            event=self.event
        )

    def test_unique_constraint_prevents_double_active_waitlist(self):
        WaitlistEntry.objects.create(user=self.user, ticket_type=self.ticket_type, position=1)
        with self.assertRaises(Exception):
            WaitlistEntry.objects.create(user=self.user, ticket_type=self.ticket_type, position=2)

    def test_unique_constraint_allows_rejoin_after_deactivation(self):
        entry = WaitlistEntry.objects.create(user=self.user, ticket_type=self.ticket_type, position=1)
        entry.is_active = False
        entry.save()
        try:
            WaitlistEntry.objects.create(user=self.user, ticket_type=self.ticket_type, position=2)
        except Exception:
            self.fail("Should allow rejoining waitlist after deactivation!")