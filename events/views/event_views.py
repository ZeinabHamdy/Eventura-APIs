from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError



from events.models.event import Event
from users.permissions import IsOrganizer
from events.serializers.event_serializer import (
    EventListSerializer,
    EventRetrieveSerializer,
    EventUpdatePublishedSerializer,
    EventUpdateStatusSerializer,
    EventWriteSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(  # Q for OR operation
            models.Q(status='published') |
            models.Q(status='cancelled') |
            models.Q(status='drafted', organizer=user)
        )

    def get_serializer_class(self):
        if self.action == 'retrieve': # get one
            return EventRetrieveSerializer
        if self.action in ['update', 'partial_update']:
            obj = self.get_object()
            if obj.status == 'published':
                return EventUpdatePublishedSerializer
            return EventWriteSerializer # drafted 
        if self.action == 'update_status':
            return EventUpdateStatusSerializer
        if self.action == 'create':
            return EventWriteSerializer
        return EventListSerializer


    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'update_status']:
            return [IsAuthenticated(), IsOrganizer()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        try:
            serializer.save(organizer=self.request.user)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)

    def perform_update(self, serializer):
        if serializer.instance.status == 'cancelled':
            raise DRFValidationError('Cannot update a cancelled event.')
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)
    
    def perform_destroy(self, instance):
        if instance.bookings.exists():
            raise DRFValidationError('Cannot delete an event that has bookings.')
        instance.delete()
        
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        event = self.get_object()
        serializer = EventUpdateStatusSerializer(event, data=request.data,partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
            except DjangoValidationError as e:
                raise DRFValidationError(e.message_dict)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)