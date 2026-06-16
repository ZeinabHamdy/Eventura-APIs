from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    rating     = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    event      = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='reviews')


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'event'],
                name='unique_review_per_user_per_event'
            )
        ]
        indexes = [
            # for get my reviews
            models.Index(fields=['user', '-rating'], name='review_user_rating_idx'),
            # for events_reviews page
            models.Index(fields=['event', '-rating'], name='review_event_rating_idx'),
            models.Index(fields=['event', '-created_at'], name='review_event_date_idx'),
        ]


    def __str__(self):
        return f'Review of {self.user.email} for event {self.event.name}'
