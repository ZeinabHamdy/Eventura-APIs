from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class PaginatedActionMixin(GenericViewSet):
    def paginated_response(self, queryset, serializer_class):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(serializer_class(queryset, many=True).data)