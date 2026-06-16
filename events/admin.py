from django.contrib import admin
from events.models import Event, Category, TicketType


admin.site.register(Category)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'organizer', 'status')
    list_filter = ('organizer', 'status', 'location_type', 'category')


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'event__organizer', 'price', 'total_seats', 'available_seats')
    list_filter =('name', 'event', 'event__organizer')