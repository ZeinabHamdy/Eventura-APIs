from django.db import models

from users.models import User

class Notification(models.Model):

    class NOTIFICATION_TYPES(models.TextChoices):
        BOOKING_CONFIRMED  = 'booking_confirmed',  'Booking Confirmed'
        BOOKING_CANCELLED  = 'booking_cancelled',  'Booking Cancelled'
        WAIT_LIST_PROMOTED = 'wait_list_promoted', 'WaitList Promoted'
        NEW_BOOKING        = 'new_booking',        'New Booking'
        EVENT_CANCELLED    = 'event_cancelled',    'Event Cancelled'
        EVENT_REMINDER     = 'event_reminder',     'Event Reminder'
        EVENT_STARTED      = 'event_started',      'Event Started'

    created_at        = models.DateTimeField(auto_now_add=True)
    message           = models.TextField()
    is_read           = models.BooleanField(default=False)
    user              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPES.choices)

    class Meta:
        ordering = ['-created_at'] 
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.get_notification_type_display()} - {self.user.email}'