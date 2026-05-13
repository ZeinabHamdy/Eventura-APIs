from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_name_length(value):
    if len(value) < 3:
        raise ValidationError('Event name must be at least 3 characters')


def validate_end_date_after_start(start_date, end_date):
    if end_date <= start_date:
        raise ValidationError('End date must be after start date')


def validate_start_date_in_future(start_date):
    if(start_date <= timezone.now()):
        raise ValidationError('Cannot make event with a past start date')


def validate_start_date_on_publish(status, new_status, start_date):
    if (new_status != status and new_status == 'published' and
        start_date <= timezone.now()):
        raise ValidationError('Cannot publish event with a past start date')


def validate_status_flow(current_status, new_status, start_date):

    # draft -> published ----- true
    # draft -> cancelled ----- true
    # published -> draft ---- false
    # published -> cancelled --- true if start_date not coming yet
    # published -> cancelled --- false if start_date in the past
    # cancelled -> stop to publish or draft

    ALLOWED = {
        'drafted':   ['published', 'cancelled'],
        'published': ['cancelled'],
        'cancelled': []
    }

    if new_status == current_status:
        return

    if new_status not in ALLOWED[current_status]:
        raise ValidationError(f'Cannot change status from {current_status} to {new_status}')

    if current_status == 'published' and new_status == 'cancelled':
        if start_date <= timezone.now():
            raise ValidationError('Cannot cancel event that has already started')