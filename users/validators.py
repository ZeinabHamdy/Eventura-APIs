from django.core.exceptions import ValidationError

def validate_username(value):
    if len(value) < 3:
        raise ValidationError('Username must be at least 3 characters')
    if ' ' in value:
        raise ValidationError('Username cannot contain spaces')
    

def validate_phone_number(value):
    if not value.startswith('+'):
        raise ValidationError('Phone number must start with +')
    if not value[1:].isdigit():
        raise ValidationError('Phone number must contain only digits after +')
    if len(value) != 13:
        raise ValidationError('Phone number must contain only 13 letter')
    