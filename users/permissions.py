from rest_framework.permissions import BasePermission
from django.apps import apps


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsOrganizer(BasePermission): 
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            event_id = request.data.get('event')
            if event_id:
                Event = apps.get_model('events', 'Event') 
                return Event.objects.filter(id=event_id, organizer=request.user).exists()
            return False 
        return True

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        if hasattr(obj, 'event'):
            return obj.event.organizer == request.user
        return False

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return obj.user == request.user or request.user.is_superuser