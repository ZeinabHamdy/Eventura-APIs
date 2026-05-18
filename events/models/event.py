from django.db import models

from events.models.category import Category
from users.models import User
from django.core.validators import MinLengthValidator

from events.validators.event_validators import(
    validate_end_date_after_start,
    validate_status_flow,
    validate_start_date_in_future,
    validate_start_date_on_publish,
)

class Event(models.Model):

    class LOCATION_TYPES(models.TextChoices):
        ONLINE  = 'online',  'Online'
        OFFLINE = 'offline', 'Offline'

    class STATUS_TYPES(models.TextChoices):
        DRAFTED   = 'drafted', 'Drafted'
        PUBLISHED = 'published', 'Published'
        CANCELLED = 'cancelled', 'Cancelled'

    name          = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    description   = models.TextField(null=True, blank=True)
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPES.choices,)
    location_link = models.URLField()
    start_date    = models.DateTimeField()
    end_date      = models.DateTimeField()
    status        = models.CharField(max_length=20, choices=STATUS_TYPES.choices, default=STATUS_TYPES.DRAFTED)
    category      = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events")  
    organizer     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.start_date and self.end_date:
            validate_end_date_after_start(self.start_date, self.end_date)

        if self.pk:   # not in creating the event (in create we can make any status)
            old_status = Event.objects.get(pk=self.pk).status
            validate_status_flow(old_status, self.status, self.start_date)
            validate_start_date_on_publish(old_status, self.status, self.start_date)
        else:
            validate_start_date_in_future(self.start_date)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name