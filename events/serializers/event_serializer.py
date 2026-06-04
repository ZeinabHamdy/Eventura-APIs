from rest_framework import serializers
from events.models.event import Event
from users.serializers import UserProfileSerializer

class EventWriteSerializer(serializers.ModelSerializer):  # for create and update the drafted events
    class Meta:
        model = Event
        fields = ['name', 'description', 'status', 'location_type', 'location_link', 'start_date', 'end_date', 'category']

class EventUpdatePublishedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['description']

    def validate(self, attrs):
        invalid_fields = set(self.initial_data.keys()) - {'description'} 
        if invalid_fields:
            raise serializers.ValidationError(
                f'Only description can be updated when event is published. Invalid fields: {invalid_fields}'
            )
        return attrs

class EventUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['status']
    
    def validate(self, attrs):
        invalid_fields = set(self.initial_data.keys()) - {'status'} # type: ignore
        if invalid_fields:
            raise serializers.ValidationError(
                f'Only status can be updated when event is published. Invalid fields: {invalid_fields}'
            )
        return attrs

class EventListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    review_count   = serializers.IntegerField(read_only=True)
    class Meta:
        model = Event
        fields = ['name', 'start_date', 'location_type', 'status', 'category', 'average_rating', 'review_count']

class EventRetrieveSerializer(serializers.ModelSerializer):
    organizer = UserProfileSerializer(read_only=True)
    category = serializers.StringRelatedField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    review_count   = serializers.IntegerField(read_only=True)
    class Meta:
        model = Event
        fields = '__all__'