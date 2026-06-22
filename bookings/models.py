from django.db import models
from django.db.models import Q


class Booking(models.Model):

    class STATUS(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    user        = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings')
    ticket_type = models.ForeignKey('events.TicketType', on_delete=models.CASCADE, related_name='bookings')
    status      = models.CharField(max_length=15, choices=STATUS.choices, default=STATUS.CONFIRMED)
    booked_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'ticket_type'],
                condition=Q(status='confirmed'),
                name='unique_confirmed_booking_per_user_per_ticket_type'
            )
        ]
        indexes = [
            models.Index(fields=['user', '-booked_at'], name='booking_user_date_idx'),
            models.Index(fields=['ticket_type', 'status'], name='booking_ticket_status_idx'),
        ]

    def clean(self):
        from bookings.validators import validate_booking_status_flow
        if self.pk:
            validate_booking_status_flow(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Booking of {self.user.email} for event {self.ticket_type.event.name}'


class WaitlistEntry(models.Model):

    user        = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='waitlist_entries')
    ticket_type = models.ForeignKey('events.TicketType', on_delete=models.CASCADE, related_name='waitlist_entries')
    position    = models.PositiveIntegerField()
    joined_at   = models.DateTimeField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'ticket_type'],
                condition=Q(is_active=True),
                name='unique_active_waitlist_per_user_per_ticket_type'
            )
        ]
        ordering = ['position']
        models.Index(
            fields=['ticket_type', 'position'], 
            name='waitlist_core_partial_idx',
            condition=models.Q(is_active=True)  
        )

    def __str__(self):
        return f'{self.user.email} → waitlist #{self.position} for {self.ticket_type.event.name}'