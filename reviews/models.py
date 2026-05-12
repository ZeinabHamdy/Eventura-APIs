from django.db import models

from users.models import User
from events.models import Event


class Review(models.Model):
    rating     = models.IntegerField()
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    event      = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return f'Review of {self.user.username} for event {self.event.name}'
