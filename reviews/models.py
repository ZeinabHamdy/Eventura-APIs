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


    def __str__(self):
        return f'Review of {self.user.email} for event {self.event.name}'
