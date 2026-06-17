from django.db import models
from events.models.event import Event
from events.validators.ticket_type_validators import(
    validate_price,
    validate_seats,
    validate_event_published_when_create_ticket_type,
)

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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'name'], 
                name='unique_ticket_type_per_event'
            )
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event', 'price'], name='ticket_event_price_idx'),
            models.Index(fields=['available_seats'], name='ticket_avail_seats_idx'),
        ]

    def clean(self):
        if self.available_seats is None:
            self.available_seats = self.total_seats
        super().clean()
        validate_seats(self.total_seats, self.available_seats)
        validate_price(self.name, self.price)
        validate_event_published_when_create_ticket_type(self.event)


    def save(self, *args, **kwargs):
        if self.available_seats is None:
            self.available_seats = self.total_seats
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.event.name} - {self.name}"