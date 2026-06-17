import datetime
from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from events.models import Event, Category, TicketType
from bookings.models import Booking, WaitlistEntry
from notifications.models import Notification
from events.tasks import (
    send_event_cancelled_notifications,
    send_event_reminder_24h_task,
    send_event_started_notifications_task
)

User = get_user_model()

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class CeleryTasksTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(email="user1@eventura.com", password="password123", phone_number='+201122334455', name='user1')
        self.user_2 = User.objects.create_user(email="user2@eventura.com", password="password123", phone_number='+201122334466', name='user2')
        self.organizer = User.objects.create_user(email="organizer@eventura.com", password="password123", phone_number='+201122334477', name='organizer')
        self.category = Category.objects.create(name="Tech")
        
        self.cancelled_event = Event.objects.create(
            name="System Design Workshop",
            description="Scalability masterclass",
            location_type="online",
            location_link='https://eventura.com/',
            status="published",
            start_date=timezone.now() + datetime.timedelta(days=5),
            end_date=timezone.now() + datetime.timedelta(days=5, hours=2),
            category=self.category,
            organizer=self.organizer
        )
        self.ticket_cancelled = TicketType.objects.create(
            event=self.cancelled_event, name="regular", price=20, total_seats=50, available_seats=50
        )
        Booking.objects.create(user=self.user_1, ticket_type=self.ticket_cancelled, status=Booking.STATUS.CONFIRMED)
        WaitlistEntry.objects.create(user=self.user_2, ticket_type=self.ticket_cancelled, is_active=True, position=1)
        
        Event.objects.filter(id=self.cancelled_event.id).update(status="cancelled")

        self.upcoming_event = Event.objects.create(
            name="Upcoming Django Workshop",
            description="Learn advanced Django",
            location_type="online",
            location_link='https://eventura.com/',
            status="published",
            start_date=timezone.now() + datetime.timedelta(hours=24, minutes=30),
            end_date=timezone.now() + datetime.timedelta(hours=26),
            category=self.category,
            organizer=self.organizer
        )
        self.ticket_upcoming = TicketType.objects.create(
            event=self.upcoming_event, name="regular", price=10, total_seats=100, available_seats=100
        )
        Booking.objects.create(user=self.user_1, ticket_type=self.ticket_upcoming, status=Booking.STATUS.CONFIRMED)

        self.started_event = Event.objects.create(
            name="Live Database Deep Dive",
            description="PostgreSQL internals",
            location_type="online",
            location_link='https://eventura.com/',
            status="published",
            start_date=timezone.now() + datetime.timedelta(hours=2),
            end_date=timezone.now() + datetime.timedelta(hours=4),
            category=self.category,
            organizer=self.organizer
        )
        self.ticket_started = TicketType.objects.create(
            event=self.started_event, name="vip", price=50, total_seats=50, available_seats=50
        )
        Booking.objects.create(user=self.user_1, ticket_type=self.ticket_started, status=Booking.STATUS.CONFIRMED)

        Event.objects.filter(id=self.started_event.id).update(
            start_date=timezone.now() - datetime.timedelta(minutes=5),
            end_date=timezone.now() + datetime.timedelta(hours=2)
        )

    def test_send_event_cancelled_notifications(self):
        self.assertFalse(Notification.objects.filter(notification_type=Notification.NOTIFICATION_TYPES.EVENT_CANCELLED).exists())
        result = send_event_cancelled_notifications.delay(self.cancelled_event.id)
        expected_msg = f"Successfully sent cancellation notifications to 2 users for event: {self.cancelled_event.name}"
        self.assertEqual(result.result, expected_msg)
        notifications = Notification.objects.filter(notification_type=Notification.NOTIFICATION_TYPES.EVENT_CANCELLED)
        self.assertEqual(notifications.count(), 2)
        target_messages = [n.message for n in notifications]
        self.assertIn(f"'{self.cancelled_event.name}' Cancelled from organizer.", target_messages)

    def test_send_event_reminder_24h_task(self):
        self.assertFalse(Notification.objects.filter(notification_type=Notification.NOTIFICATION_TYPES.EVENT_REMINDER).exists())
        result = send_event_reminder_24h_task.delay()
        self.assertEqual(result.result, "Sent 24h reminders to 1 users.")
        notification = Notification.objects.filter(notification_type=Notification.NOTIFICATION_TYPES.EVENT_REMINDER).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user_1)
        self.assertEqual(notification.message, "Reminder: Your event starts in 24 hours")

    def test_send_event_started_notifications_task(self):
        self.assertFalse(Notification.objects.filter(notification_type=Notification.NOTIFICATION_TYPES.EVENT_STARTED).exists())
        result = send_event_started_notifications_task.delay()
        self.assertEqual(result.result, "Sent 'Event Started' notifications to 1 users.")
        notification = Notification.objects.filter(notification_type=Notification.NOTIFICATION_TYPES.EVENT_STARTED).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user_1)
        self.assertEqual(notification.message, f"Event started already '{self.started_event.name}' !!")