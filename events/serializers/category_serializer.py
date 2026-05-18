from rest_framework import serializers

from events.models.category import Category
from events.serializers.event_serializer import EventListSerializer


class CategorySerializer(serializers.ModelSerializer):
    events = EventListSerializer(many=True, read_only=True) # nested serializers
    # events -> related name
    class Meta:
        model = Category
        fields = ['id', 'name', 'events']