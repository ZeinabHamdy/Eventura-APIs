from django_filters import rest_framework as filters

from events.models.ticket_type import TicketType
from events.models.event import Event


class EventFilter(filters.FilterSet):
    start_date_after  = filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = filters.DateTimeFilter(field_name='start_date', lookup_expr='lte')

    class Meta:
        model  = Event
        fields = ['status', 'category', 'location_type']




class TicketTypeFilter(filters.FilterSet):
    min_price        = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price        = filters.NumberFilter(field_name='price', lookup_expr='lte')
    available_seats  = filters.NumberFilter(field_name='available_seats', lookup_expr='gte')

    class Meta:
        model  = TicketType
        fields = ['name', 'event']
