from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bookings.models import Booking, WaitlistEntry
from bookings.serializers import BookingReadSerializer, BookingCreateSerializer, WaitlistReadSerializer
from bookings.services import create_booking_or_join_waitlist, cancel_booking
from users.permissions import IsOwnerOrAdmin
from utils.mixins import PaginatedActionMixin



class BookingViewSet(PaginatedActionMixin, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.all()
        return qs if user.is_superuser else qs.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingReadSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) # BookingCreateSerializer
        serializer.is_valid(raise_exception=True)

        ticket_type = serializer.validated_data['ticket_type']

        try:
            result_type, instance = create_booking_or_join_waitlist(request.user, ticket_type)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)

        if result_type == 'booking':
            return Response(
                BookingReadSerializer(instance).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'detail': 'No seats available. You have been added to the waitlist.',
                'waitlist': WaitlistReadSerializer(instance).data,
            },
            status=status.HTTP_202_ACCEPTED
        )


    @action(detail=False, methods=['get'], url_path='event/(?P<event_pk>[^/.]+)',)
    def event_bookings(self, request, event_pk=None):
        from events.models import Event

        try:
            event = Event.objects.get(pk=event_pk)
        except Event.DoesNotExist:
            return Response(
                {'detail': 'Event not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if event.organizer != request.user and not request.user.is_superuser:
            return Response(
                {'detail': 'Not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = Booking.objects.filter(
            ticket_type__event=event,
            status=Booking.STATUS.CONFIRMED
        )
        return self.paginated_response(bookings, BookingReadSerializer)


    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status == Booking.STATUS.CANCELLED:
            return Response(
                {'detail': 'Booking is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cancel_booking(booking)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)

        return Response({'detail': 'Booking cancelled successfully.'})






class WaitlistViewSet(PaginatedActionMixin,mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WaitlistReadSerializer

    def get_queryset(self):
        user = self.request.user
        qs = WaitlistEntry.objects.filter(is_active=True)
        return qs if user.is_superuser else qs.filter(user=user)

    def perform_destroy(self, instance):
        instance.is_active = False  # not delete in database
        instance.save(update_fields=['is_active'])


    @action(detail=False, methods=['get'], url_path='event/(?P<event_pk>[^/.]+)',)
    def event_waitlist(self, request, event_pk=None):
        from events.models import Event

        try:
            event = Event.objects.get(pk=event_pk)
        except Event.DoesNotExist:
            return Response(
                {'detail': 'Event not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if event.organizer != request.user and not request.user.is_superuser:
            return Response(
                {'detail': 'Not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        waitlist = WaitlistEntry.objects.filter(
            ticket_type__event=event,
            is_active=True
        ).order_by('position')

        return self.paginated_response(waitlist, WaitlistReadSerializer)