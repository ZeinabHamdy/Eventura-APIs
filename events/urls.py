from django.urls import path, include
from rest_framework.routers import DefaultRouter
from events.views.category_views import CategoryViewSet
from events.views.event_views import EventViewSet
from events.views.ticket_type_views import TicketTypeViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('events', EventViewSet, basename='event')
router.register('ticket-types', TicketTypeViewSet, basename='ticket-types')

urlpatterns = [
    path('', include(router.urls)), 
]