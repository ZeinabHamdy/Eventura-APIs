from django.db import models
from events.models import Event


class TicketType(models.Model):

    class TICKET_TYPES(models.TextChoices):
        #value  = db_value, display name
        VIP     = 'vip', 'VIP'
        REGULAR = 'regular', 'Regular'
        FREE    = 'free', 'Free'

    name            = models.CharField(max_length=10, choices = TICKET_TYPES.choices)
    price           = models.DecimalField(max_digits=8, decimal_places=2)
    total_seats     = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    event           = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.name} - {self.name}"