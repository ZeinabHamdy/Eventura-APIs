import re
from django.core.exceptions import ValidationError

def validate_phone_number(value):
    if not value: 
        return
    phone_regex = r'^\+\d{12}$'
    if not re.match(phone_regex, value):
        raise ValidationError('Phone number must start with + and contain exactly 12 digits after it.')