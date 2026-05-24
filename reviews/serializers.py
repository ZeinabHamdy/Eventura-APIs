from rest_framework import serializers

from reviews.models import Review



class CreateReviewSerializer(serializers.ModelSerializer):

    def validate_event(self, event):
        from reviews.validators import(
            validate_after_end_date, 
            validate_confirmed_booking,
            validate_no_existing_review,
            validate_not_organizer,
            validate_published_event,
        )
        user = self.context['request'].user 
        validate_published_event(event)
        validate_not_organizer(user, event)
        validate_after_end_date(event)
        # put database queries in the end to avoid extra queries
        validate_confirmed_booking(user, event)
        validate_no_existing_review(user, event)
        return event


    class Meta:
        model = Review
        fields = ['event', 'rating', 'comment']


class UpdateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']



class ListReviewSerializer(serializers.ModelSerializer):
    user  = serializers.EmailField(source='user.email', read_only=True)
    event = serializers.CharField(source='event.name', read_only=True)
    class Meta:
        model = Review
        fields = ['user', 'event', 'rating', 'comment', 'created_at']