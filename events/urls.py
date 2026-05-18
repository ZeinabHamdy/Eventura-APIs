from django.urls import path, include
from rest_framework.routers import DefaultRouter
from events.views.category_views import CategoryViewSet
from events.views.event_views import EventViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)), 
]