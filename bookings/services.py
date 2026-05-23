from django.db import transaction
from bookings.models import Booking, WaitlistEntry


def _create_booking(user, ticket_type):
    ticket_type.available_seats -= 1
    ticket_type.save(update_fields=['available_seats'])

    booking = Booking.objects.create(
        user=user,
        ticket_type=ticket_type,
    )
    return ('booking', booking)


def _join_waitlist(user, ticket_type):
    last = WaitlistEntry.objects.filter(
        ticket_type=ticket_type,
        is_active=True
    ).order_by('-position').first()

    position = (last.position + 1) if last else 1

    entry = WaitlistEntry.objects.create(
        user=user,
        ticket_type=ticket_type,
        position=position,
    )
    return ('waitlist', entry)

@transaction.atomic  # all or nothing
def create_booking_or_join_waitlist(user, ticket_type):
    # select for update for race condition <==
    ticket_type = ticket_type.__class__.objects.select_for_update().get(pk=ticket_type.pk)

    if ticket_type.available_seats > 0:
        return _create_booking(user, ticket_type)
    else:
        return _join_waitlist(user, ticket_type)




@transaction.atomic
def cancel_booking(booking):
    ticket_type = booking.ticket_type.__class__.objects.select_for_update().get(
        pk=booking.ticket_type.pk
    )

    booking.status = Booking.STATUS.CANCELLED
    booking.save()


    # get first person in waitlist
    next_in_line = WaitlistEntry.objects.select_for_update().filter(
        ticket_type=ticket_type,
        is_active=True
    ).order_by('position').first()

    if next_in_line:
        _promote_from_waitlist(next_in_line, ticket_type)
    else:
        ticket_type.available_seats += 1
        ticket_type.save(update_fields=['available_seats'])


def _promote_from_waitlist(entry, ticket_type):
    entry.is_active = False
    entry.save(update_fields=['is_active'])

    Booking.objects.create(
        user=entry.user,
        ticket_type=ticket_type,
    )
    ##### notification need here
    
