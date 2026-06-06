from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from users.models import User
from events.models.category import Category
from events.models.event import Event
from reviews.models import Review

class ReviewsModelTestCase(TestCase):
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
    def test_unique_constraint_prevents_double_review_for_same_event(self):
        Review.objects.create(user=self.user, rating=3, comment='good', event = self.event)
        with self.assertRaises(Exception):
            Review.objects.create(user=self.user, rating=3, comment='good', event = self.event)