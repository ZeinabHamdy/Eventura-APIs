from rest_framework.response import Response
from rest_framework import status, viewsets
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Count



from events.filters import TicketTypeFilter
from events.models.ticket_type import TicketType
from events.serializers.ticket_type_serializer import(
    TicketTypeCreateSerializer,
    TicketTypeReadSerializer,
    TicketTypeUpdateSerializer,
    TicketTypeUpdateWithBookingSerializer,
)



class TicketTypeViewSet(viewsets.ModelViewSet):
    queryset = TicketType.objects.select_related('event').annotate( # N+1 problem solved
        bookings_count=Count('bookings')
    ).all().order_by('id')
    filter_backends  = [DjangoFilterBackend, OrderingFilter]
    filterset_class  = TicketTypeFilter
    ordering_fields  = ['price', 'available_seats']

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketTypeCreateSerializer
        if self.action in ['update', 'partial_update']:
            instance = self.get_object()
            if instance.bookings_count > 0: 
                return TicketTypeUpdateWithBookingSerializer
            return TicketTypeUpdateSerializer
        return TicketTypeReadSerializer

    def perform_update(self, serializer):
        try:
            instance = serializer.instance 
            if instance.bookings_count > 0: 
                new_total = serializer.validated_data.get('total_seats', instance.total_seats)
                booked = instance.total_seats - instance.available_seats 
                if booked > new_total:
                    raise DRFValidationError(f'Cannot set total seats to {new_total}, already {booked} seats booked.')
                serializer.save(available_seats=new_total - booked)
            else:
                total_seats = serializer.validated_data.get('total_seats', instance.total_seats)
                serializer.save(available_seats=total_seats)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)

    def perform_destroy(self, instance):
        if instance.bookings_count > 0: 
            raise DRFValidationError('Cannot delete a ticket type that has bookings.')
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.bookings.exists(): 
            return Response(
                {"detail": "Cannot delete ticket type with active bookings."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        event_id = request.data.get('event')
        if event_id:
            from events.models import Event
            event = Event.objects.get(pk=event_id)
            if event.organizer != request.user:
                return Response({"detail": "You are not the organizer."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)