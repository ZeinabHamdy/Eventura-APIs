from rest_framework import serializers

from bookings.models import Booking, WaitlistEntry


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model= Booking
        fields= ['ticket_type']

    def validate_ticket_type(self, ticket_type):
        from bookings.validators import (
            validate_event_published,
            validate_event_not_started,
            validate_not_organizer,
            validate_no_active_booking,
            validate_not_already_in_waitlist,
        )
        user = self.context['request'].user

        validate_event_published(ticket_type)
        validate_event_not_started(ticket_type)
        validate_not_organizer(user, ticket_type)
        validate_no_active_booking(user, ticket_type)
        validate_not_already_in_waitlist(user, ticket_type)

        return ticket_type


class BookingReadSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='ticket_type.event.name', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    price = serializers.DecimalField(source='ticket_type.price', max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model= Booking
        fields= ['id', 'ticket_type', 'event_name', 'ticket_type_name', 'price', 'status', 'booked_at',]


class WaitlistReadSerializer(serializers.ModelSerializer):
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    event_name       = serializers.CharField(source='ticket_type.event.name', read_only=True)

    class Meta:
        model  = WaitlistEntry
        fields = ['id', 'ticket_type', 'ticket_type_name', 'event_name', 'position', 'joined_at']