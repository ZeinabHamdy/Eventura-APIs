from django.db import models

from events.models import Category
from users.models import User


class Event(models.Model):

    class LOCATION_TYPES(models.TextChoices):
        ONLINE  = 'online',  'Online'
        OFFLINE = 'offline', 'Offline'

    class STATUS_TYPES(models.TextChoices):
        DRAFTED   = 'drafted', 'Drafted'
        PUBLISHED = 'published', 'Published'
        CANCELLED = 'cancelled', 'Cancelled'

    name          = models.CharField(max_length=100)
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

    def __str__(self):
        return self.name