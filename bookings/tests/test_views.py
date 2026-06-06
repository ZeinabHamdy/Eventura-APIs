from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User
from events.models.category import Category
from events.models.event import Event
from events.models.ticket_type import TicketType
from bookings.models import Booking, WaitlistEntry


class BookingViewSetTestCase(APITestCase):
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
        self.other_user = User.objects.create_user(
            email='other@eventura.com',
            password='Password1234',
            name='Other User',
            phone_number='+201122334477'
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

    """ happy paths """

    def test_create_booking_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/bookings/', {'ticket_type': self.ticket_type.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.ticket_type.refresh_from_db()
        self.assertEqual(self.ticket_type.available_seats, 9)

    def test_create_booking_joins_waitlist_when_no_seats(self):
        self.ticket_type.available_seats = 0
        self.ticket_type.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/bookings/', {'ticket_type': self.ticket_type.id})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(WaitlistEntry.objects.filter(user=self.user, ticket_type=self.ticket_type).exists())

    def test_cancel_booking_returns_seat(self):
        self.client.force_authenticate(user=self.user)
        self.ticket_type.available_seats = 9
        self.ticket_type.save()
        booking = Booking.objects.create(user=self.user, ticket_type=self.ticket_type)
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket_type.refresh_from_db()
        self.assertEqual(self.ticket_type.available_seats, 10)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS.CANCELLED)

    def test_cancel_booking_promotes_first_in_waitlist(self):
        booking = Booking.objects.create(user=self.other_user, ticket_type=self.ticket_type)
        self.ticket_type.available_seats = 0
        self.ticket_type.save()
        WaitlistEntry.objects.create(user=self.user, ticket_type=self.ticket_type, position=1)
        self.client.force_authenticate(user=self.other_user)
        self.client.post(f'/api/bookings/{booking.id}/cancel/')
        self.assertTrue(Booking.objects.filter(
            user=self.user,
            ticket_type=self.ticket_type,
            status=Booking.STATUS.CONFIRMED
        ).exists())
        self.assertFalse(WaitlistEntry.objects.filter(
            user=self.user,
            ticket_type=self.ticket_type,
            is_active=True
        ).exists())
        self.ticket_type.refresh_from_db()
        self.assertEqual(self.ticket_type.available_seats, 0)




    """ unhappy paths """

    def test_unauthenticated_user_cannot_book(self):
        response = self.client.post('/api/bookings/', {'ticket_type': self.ticket_type.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_organizer_cannot_book_own_event(self):
        self.client.force_authenticate(user=self.organizer)
        response = self.client.post('/api/bookings/', {'ticket_type': self.ticket_type.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_book_started_event(self):
        self.event.start_date = timezone.now() - timedelta(hours=1)
        self.event.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/bookings/', {'ticket_type': self.ticket_type.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_book_twice(self):
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/bookings/', {'ticket_type': self.ticket_type.id})
        response = self.client.post('/api/bookings/', {'ticket_type': self.ticket_type.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_already_cancelled_booking(self):
        booking = Booking.objects.create(user=self.user, ticket_type=self.ticket_type)
        booking.status = Booking.STATUS.CANCELLED
        booking.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)