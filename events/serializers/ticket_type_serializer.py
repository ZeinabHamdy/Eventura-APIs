from rest_framework import serializers

from events.models.ticket_type import TicketType


class TicketTypeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = '__all__'


class TicketTypeUpdateSerializer(serializers.ModelSerializer):
    # in update(when not exist bookings yet)
    available_seats = serializers.IntegerField(read_only=True)
    class Meta:
        model = TicketType
        fields = ['name', 'price', 'total_seats', 'available_seats']


class TicketTypeCreateSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(read_only=True)
    class Meta:
        model = TicketType
        fields = ['name', 'price', 'total_seats', 'event', 'available_seats']


class TicketTypeUpdateWithBookingSerializer(serializers.ModelSerializer):
    # when update ticket but there exist people booked it!!! 
    # organizer should be update in total seats only
    class Meta:
        model = TicketType
        fields = ['total_seats']

    def validate(self, attrs):
        invalid_fields = set(self.initial_data.keys()) - {'total_seats'} # type: ignore
        if invalid_fields:
            raise serializers.ValidationError(
                f'Only total_seats can be updated. Invalid fields: {invalid_fields}'
            )
        return attrs