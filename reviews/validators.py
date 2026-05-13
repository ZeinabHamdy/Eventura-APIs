from django.core.exceptions import ValidationError
from django.utils import timezone



def validate_not_organizer(review):
    if review.user == review.event.organizer:
        raise ValidationError("Organizer can't review his event")


def validate_after_end_date(end_date):
    if timezone.now() < end_date:
        raise ValidationError("Can't review event before its end")


def validate_no_existing_review(user, event):
    from reviews.models import Review

    if Review.objects.filter(user=user, event=event).exists():
        raise ValidationError("Already reviewed this event")


def validate_confirmed_booking(user, event):
    from bookings.models import Booking
    
    if not Booking.objects.filter(user=user, ticket_type__event=event, status='confirmed').exists():
        raise ValidationError("You must have a confirmed booking to review this event")

def validate_published_event(event):
    if event.status != 'published':
        raise ValidationError("No event found")