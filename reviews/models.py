from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from events.models import Event

from reviews.validators import(
    validate_confirmed_booking,
    validate_not_organizer,
    validate_after_end_date,
    validate_no_existing_review,
    validate_published_event,
)


class Review(models.Model):
    rating     = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    event      = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')


    def clean(self):
        validate_not_organizer(self)
        validate_after_end_date(self.event.end_date)
        validate_no_existing_review(self.user, self.event)
        validate_confirmed_booking(self.user, self.event)
        validate_published_event(self.event)


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f'Review of {self.user.username} for event {self.event.name}'
