import datetime

from django.db import transaction
from src.celery import app
from django.utils import timezone


from events.models.event import Event
from bookings.models import Booking, WaitlistEntry 
from notifications.models import Notification

@app.task
def send_event_cancelled_notifications(event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return f"Event {event_id} not found."

    # distinct -> as some people may book from all ticket type (send one notification only)
    booking_user_ids = Booking.objects.filter(
        ticket_type__event=event
    ).exclude(
        status='cancelled'
    ).values_list('user_id', flat=True).distinct()

    waitlist_user_ids = WaitlistEntry.objects.filter(
        ticket_type__event=event,
        is_active=True
    ).values_list('user_id', flat=True).distinct()

    all_target_user_ids = set(list(booking_user_ids) + list(waitlist_user_ids))

    if not all_target_user_ids:
        return f"No active users to notify for cancelled event: {event.name}"

    notifications_to_create = []
    message_content = f"'{event.name}' Cancelled from organizer."

    for user_id in all_target_user_ids:
        notifications_to_create.append(
            Notification(
                user_id=user_id,
                message=message_content,
                notification_type=Notification.NOTIFICATION_TYPES.EVENT_CANCELLED
            )
        )

    with transaction.atomic():
        Notification.objects.bulk_create(notifications_to_create)

    return f"Successfully sent cancellation notifications to {len(notifications_to_create)} users for event: {event.name}"





# celery beat scheduled

@app.task
def send_event_reminder_24h_task():
    now = timezone.now()
    tomorrow_start = now + datetime.timedelta(hours=24)
    tomorrow_end = now + datetime.timedelta(hours=25)
    # get any event published in this interval
    upcoming_events = Event.objects.filter(
        status='published',
        start_date__gte=tomorrow_start,
        start_date__lte=tomorrow_end
    )
    if not upcoming_events.exists():
        return "No events starting in the next 24 hours."

    notifications_to_create = []
    for event in upcoming_events:
        user_ids = Booking.objects.filter(
            ticket_type__event=event,
            status=Booking.STATUS.CONFIRMED 
        ).values_list('user_id', flat=True).distinct()

        for user_id in user_ids:
            notifications_to_create.append(
                Notification(
                    user_id=user_id,
                    message=f"Reminder! the event '{event.name}' will start after 24 hours !",
                    notification_type=Notification.NOTIFICATION_TYPES.EVENT_REMINDER
                )
            )

    if notifications_to_create:
        with transaction.atomic():
            Notification.objects.bulk_create(notifications_to_create)
        return f"Sent 24h reminders to {len(notifications_to_create)} users."
    
    return "No active bookings found for upcoming events."



@app.task
def send_event_started_notifications_task():
    now = timezone.now()
    fifteen_minutes_ago = now - datetime.timedelta(minutes=15)
    started_events = Event.objects.filter(
        status='published',
        start_date__gte=fifteen_minutes_ago,
        start_date__lte=now
    )

    if not started_events.exists():
        return "No events started in this window."

    notifications_to_create = []

    for event in started_events:
        user_ids = Booking.objects.filter(
            ticket_type__event=event,
            status=Booking.STATUS.CONFIRMED
        ).values_list('user_id', flat=True).distinct()

        for user_id in user_ids:
            notifications_to_create.append(
                Notification(
                    user_id=user_id,
                    message=f"Event started already '{event.name}' !!",
                    notification_type=Notification.NOTIFICATION_TYPES.EVENT_STARTED 
                )
            )

    if notifications_to_create:
        with transaction.atomic():
            Notification.objects.bulk_create(notifications_to_create)
        return f"Sent 'Event Started' notifications to {len(notifications_to_create)} users."

    return "No active participants to notify for started events."