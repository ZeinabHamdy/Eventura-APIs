from django.db import models

from events.models import TicketType
from users.models import User

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

    def __str__(self):
        return f'Booking of {self.user.username} of event {self.ticket_type.event.name}'