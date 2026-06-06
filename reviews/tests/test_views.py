from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User
from events.models.category import Category
from events.models.event import Event
from events.models.ticket_type import TicketType
from reviews.models import Review



class ReviewViewSetTesting(APITestCase):
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

    """ Happy paths:- """
    def test_create_review_success(self):
        Event.objects.filter(id=self.event.id).update(
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() - timedelta(days=1)
        )
        from bookings.models import Booking
        Booking.objects.create(user=self.user, ticket_type=self.ticket_type, status='confirmed')
        self.client.force_authenticate(user=self.user)
        data = {
            "event": self.event.id,
            "rating": 3,
            "comment": 'good'
        }
        response = self.client.post('/api/reviews/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(event=self.event).exists())

    def test_get_reviews_success(self):
        review = Review.objects.create(
            event=self.event,
            user=self.user,
            rating=4,
            comment="Amazing event!"
        ) 
        self.client.force_authenticate(user=self.user)
        response_list = self.client.get('/api/reviews/')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        response_detail = self.client.get(f'/api/reviews/{review.id}/')
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response_detail.data['comment'], "Amazing event!")

    def test_update_review_success(self):
        review = Review.objects.create(
            event=self.event,
            user=self.user,
            rating=3,
            comment="It was okay."
        )
        self.client.force_authenticate(user=self.user)
        update_data = {
            "rating": 5,
            "comment": "Changed my mind, it was perfect!"
        }
        response = self.client.patch(f'/api/reviews/{review.id}/', data=update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Changed my mind, it was perfect!")

    def test_delete_review_success(self):
        review = Review.objects.create(
            event=self.event,
            user=self.user,
            rating=2,
            comment="Not my type."
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/reviews/{review.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())


    """ unhappy paths: """


    def test_organizer_cannot_review_own_event_raises_fail(self):
        Event.objects.filter(id=self.event.id).update(
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() - timedelta(days=1)
        )
        self.client.force_authenticate(user=self.organizer)
        data = {"event": self.event.id, "rating": 5, "comment": "My event is awesome!"}
        response = self.client.post('/api/reviews/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_user_without_confirmed_booking_cannot_review_raises_fail(self):
        Event.objects.filter(id=self.event.id).update(
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() - timedelta(days=1)
        )
        self.client.force_authenticate(user=self.other_user)
        data = {"event": self.event.id, "rating": 4, "comment": "I didn't attend but I want to review."}
        response = self.client.post('/api/reviews/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_review_before_event_ends_raises_fail(self):
        Event.objects.filter(id=self.event.id).update(
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2)
        )
        from bookings.models import Booking
        Booking.objects.create(user=self.user, ticket_type=self.ticket_type, status='confirmed')
        self.client.force_authenticate(user=self.user)
        data = {"event": self.event.id, "rating": 4, "comment": "Reviewing early!"}
        response = self.client.post('/api/reviews/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_cannot_review_same_event_twice_raises_fail(self):
        Event.objects.filter(id=self.event.id).update(
            start_date=timezone.now() - timedelta(days=2),
            end_date=timezone.now() - timedelta(days=1)
        )
        from bookings.models import Booking
        Booking.objects.create(user=self.user, ticket_type=self.ticket_type, status='confirmed')
        Review.objects.create(event=self.event, user=self.user, rating=4, comment="First review")
        self.client.force_authenticate(user=self.user)
        data = {"event": self.event.id, "rating": 5, "comment": "Second review"}
        response = self.client.post('/api/reviews/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_update_another_users_review_raises_fail(self):
        review = Review.objects.create(event=self.event, user=self.user, rating=3, comment="User's review")
        self.client.force_authenticate(user=self.other_user)
        update_data = {"rating": 5, "comment": "Hacking this review!"}
        response = self.client.patch(f'/api/reviews/{review.id}/', data=update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)