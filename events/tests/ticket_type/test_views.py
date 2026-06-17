from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from users.models import User
from bookings.models import Booking
from events.models import Event, Category, TicketType

class TicketTypeViewsIntegrationTesting(APITestCase):
    def setUp(self):
        self.organizer = User.objects.create(
            name='organizer',
            email='organizer@eventura.com',
            phone_number='+201122334455',
            password='organizer1234'
        )
        self.organizer2 = User.objects.create(
            name='organizer2',
            email='organizer2@eventura.com',
            phone_number='+201122334466',
            password='organizer21234'
        )
        self.user = User.objects.create(
            name='user',
            email='user@eventura.com',
            phone_number='+201122334477',
            password='user1234'
        )
        self.now = timezone.now()
        self.category = Category.objects.create(name='Tech')
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

        self.list_url = reverse('ticket-types-list')

    def _create_ticket_type(self, event, name="regular", price=100.00, total_seats=50, available_seats=50):
        return TicketType.objects.create(
            event=event, name=name, price=price, total_seats=total_seats, available_seats=available_seats
        )

    def test_anonymous_user_cannot_create_ticket_type(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_normal_user_cannot_create_ticket_type(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "regular",
            "price": "150.00",
            "total_seats": 100,
            "event": self.published_event.pk
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_list_ticket_types(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_ticket_type_success(self):
        self.client.force_authenticate(user=self.organizer)
        data = {
            "name": "regular",
            "price": "150.00",
            "total_seats": 100,
            "event": self.published_event.pk
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ticket = TicketType.objects.get(event=self.published_event, name="regular")
        self.assertEqual(ticket.available_seats, 100)

    def test_update_ticket_type_without_bookings_success(self):
        ticket = self._create_ticket_type(event=self.published_event, name="regular", total_seats=50)
        url = reverse('ticket-types-detail', kwargs={'pk': ticket.pk})
        self.client.force_authenticate(user=self.organizer)
        data = {
            "name": "vip",
            "price": "300.00",
            "total_seats": 60
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.name, "vip")
        self.assertEqual(ticket.available_seats, 60)

    def test_update_total_seats_with_bookings_success(self):
        ticket = self._create_ticket_type(event=self.published_event, total_seats=50, available_seats=50) 
        url = reverse('ticket-types-detail', kwargs={'pk': ticket.pk})
        Booking.objects.create(user=self.user, ticket_type=ticket, status="confirmed")
        ticket.available_seats = 49 
        ticket.save()
        self.client.force_authenticate(user=self.organizer)
        data = {"total_seats": 100}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.total_seats, 100)
        self.assertEqual(ticket.available_seats, 99)


    def test_update_total_seats_less_than_booked_raises_error(self):
        ticket = self._create_ticket_type(event=self.published_event, total_seats=50, available_seats=50)
        url = reverse('ticket-types-detail', kwargs={'pk': ticket.pk})
        Booking.objects.create(user=self.user, ticket_type=ticket, status="confirmed")
        ticket.available_seats = 30 
        ticket.save()

        self.client.force_authenticate(user=self.organizer)
        response = self.client.patch(url, {'total_seats': 15}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot set total seats to 15', str(response.data))


    def test_delete_ticket_type_without_bookings_success(self):
        ticket = self._create_ticket_type(event=self.published_event)
        url = reverse('ticket-types-detail', kwargs={'pk': ticket.pk})
        self.client.force_authenticate(user=self.organizer)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TicketType.objects.filter(pk=ticket.pk).exists())

    def test_delete_ticket_type_with_bookings_raises_error(self):
        ticket = self._create_ticket_type(event=self.published_event)
        url = reverse('ticket-types-detail', kwargs={'pk': ticket.pk})
        with patch('django.db.models.query.QuerySet.exists', return_value=True):
            self.client.force_authenticate(user=self.organizer)
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('Cannot delete ticket type with active bookings.', str(response.data))

    def test_filter_and_order_ticket_types(self):
        self._create_ticket_type(event=self.published_event, name="free", price=0.00)
        self._create_ticket_type(event=self.published_event, name="regular", price=100.00)
        self._create_ticket_type(event=self.published_event, name="vip", price=500.00)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'min_price': 50, 'max_price': 200})
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'regular')
        response = self.client.get(self.list_url, {'ordering': '-price'})
        results = response.data.get('results', response.data)
        self.assertEqual(results[0]['name'], 'vip')