from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError


from reviews.serializers import(
    CreateReviewSerializer,
    ListReviewSerializer,
    UpdateReviewSerializer,
)
from reviews.models import Review
from utils.mixins import PaginatedActionMixin


class ReviewViewSet(PaginatedActionMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReviewSerializer
        if self.action in ['update', 'partial_update']: 
            return UpdateReviewSerializer
        return ListReviewSerializer
    
    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict)
        
    @action(detail=False, methods=['get'], url_path='event/(?P<event_pk>[^/.]+)',)
    def event_reviews(self, request, event_pk=None):
        from events.models import Event
        try:
            event = Event.objects.get(pk=event_pk)
        except Event.DoesNotExist:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        reviews = Review.objects.filter(event=event)
        return self.paginated_response(reviews, ListReviewSerializer)