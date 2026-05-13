from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_not_organizer(booking):
    if booking.user == booking.ticket_type.event.organizer:
        raise ValidationError("Organizer can't book his own event")

def validate_not_published(status):
    if status != 'published':
        raise ValidationError("Can't book unpublished event")

def validate_start_date(start_date):
    if start_date <= timezone.now():
        raise ValidationError("Can't book event that already started")

def validate_no_existing_booking(booking):
    from bookings.models import Booking  
    
    if Booking.objects.filter(
        user=booking.user,
        ticket_type__name=booking.ticket_type.name,
        ticket_type__event=booking.ticket_type.event,
        status__in=['confirmed', 'wait_list'],
    ).exists():
        raise ValidationError("Already booked this event")
    
