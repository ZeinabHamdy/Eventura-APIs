from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.filters import OrderingFilter


from reviews.serializers import(
    CreateReviewSerializer,
    ListReviewSerializer,
    UpdateReviewSerializer,
)
from reviews.models import Review
from utils.mixins import PaginatedActionMixin

from drf_spectacular.utils import extend_schema
@extend_schema(tags=['8. Reviews'])
class ReviewViewSet(PaginatedActionMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [OrderingFilter]
    ordering_fields  = ['rating','created_at']
    ordering         = ['-rating']


    def get_queryset(self):
        return Review.objects.select_related('user', 'event').filter(user=self.request.user) # N+1 problem solved
    
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
        reviews = Review.objects.select_related('user', 'event').filter(event=event) # N+1 problem solved
        reviews = self.filter_queryset(reviews)
        return self.paginated_response(reviews, ListReviewSerializer)