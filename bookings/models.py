from django.db import models

from events.models.ticket_type import TicketType
from users.models import User
from bookings.validators import (
    validate_not_published,
    validate_not_organizer,
    validate_start_date,
    validate_no_existing_booking,
)

class Booking(models.Model):

    class BOOKING_STATUS(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        WAIT_LIST = 'wait_list', 'Wait List'

    booked_at   = models.DateTimeField(auto_now_add=True)
    status      = models.CharField(max_length=15, choices=BOOKING_STATUS.choices)
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='bookings' )
    #qr_code   = 


    def clean(self):
        validate_start_date(self.ticket_type.event.start_date)
        validate_not_organizer(self)
        validate_not_published(self.ticket_type.event.status)
        validate_no_existing_booking(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Booking of {self.user.username} of event {self.ticket_type.event.name}'