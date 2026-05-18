from django.core.exceptions import ValidationError



def validate_seats(total_seats, available_seats):
    if available_seats > total_seats:
        raise ValidationError("Available seats can't be more than total seats")
    
    if total_seats < 1 :
        raise ValidationError("Total seats must be at least 1")


def validate_event_published(event):
    if event.status != 'published':
        raise ValidationError("Cannot create ticket type for unpublished event")
    

def validate_price(name, price):
    if name == 'free' and price != 0:
        raise ValidationError("Free ticket price must be 0")
    
    if name != 'free' and price <= 0:
        raise ValidationError("Price must be positive")


def validate_unique_ticket_type_per_event(event, name, pk=None):
    from events.models.ticket_type import TicketType
    qs = TicketType.objects.filter(event=event, name=name)
    if pk:
        qs = qs.exclude(pk=pk)
    if qs.exists():
        raise ValidationError(f'Event already has a {name} ticket type')