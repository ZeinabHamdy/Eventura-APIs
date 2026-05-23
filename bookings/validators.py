from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_event_published(ticket_type):
    if ticket_type.event.status != 'published':
        raise ValidationError("Can't book unpublished event.")


def validate_event_not_started(ticket_type):
    if ticket_type.event.start_date <= timezone.now():
        raise ValidationError("Can't book an event that already started.")


def validate_not_organizer(user, ticket_type):
    if user == ticket_type.event.organizer:
        raise ValidationError("Organizer can't book their own event.")


def validate_no_active_booking(user, ticket_type):
    from bookings.models import Booking
    if Booking.objects.filter(
        user=user,
        ticket_type=ticket_type,
        status='confirmed'
    ).exists():
        raise ValidationError("You already have an active booking for this ticket type.")


def validate_not_already_in_waitlist(user, ticket_type):
    from bookings.models import WaitlistEntry
    if WaitlistEntry.objects.filter(
        user=user,
        ticket_type=ticket_type,
        is_active=True
    ).exists():
        raise ValidationError("You are already in the waitlist for this ticket type.")


def validate_booking_status_flow(booking):
    old = booking.__class__.objects.get(pk=booking.pk)
    if old.status == 'cancelled' and booking.status == 'confirmed':
        raise ValidationError("Cannot reactivate a cancelled booking.")