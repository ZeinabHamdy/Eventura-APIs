from django.contrib import admin
from bookings.models import Booking, WaitlistEntry


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_event', 'ticket_type', 'status')
    list_select_related = ('user', 'ticket_type__event')
    list_filter = ['status'] 
    search_fields = ['user__email', 'ticket_type__event__name']

    def get_event(self, obj):
        return obj.ticket_type.event.name


@admin.register(WaitlistEntry)
class WaitListAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticket_type', 'get_event', 'is_active')
    list_select_related = ('user', 'ticket_type__event')
    list_filter = ['is_active'] 
    search_fields = ['user__email', 'ticket_type__event__name']

    def get_event(self, obj):
        return obj.ticket_type.event.name