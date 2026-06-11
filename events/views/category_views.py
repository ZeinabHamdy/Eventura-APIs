from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminUser
from rest_framework.filters import SearchFilter

from events.models.category import Category
from events.serializers.category_serializer import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.prefetch_related('events').all().order_by('id') # N+1 problem solved
    serializer_class = CategorySerializer
    http_method_names=['get', 'post', 'delete']
    filter_backends = [SearchFilter]
    search_fields   = ['name']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
