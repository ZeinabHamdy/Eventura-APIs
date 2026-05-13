from django.db import models
from django.contrib.auth.models import AbstractUser

from users.validators import (
    validate_phone_number,
    validate_username,
)

class User(AbstractUser):
    name         = models.CharField(max_length=50)
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=13, unique=True, validators=[validate_phone_number])
    is_admin     = models.BooleanField(default=False)
    username     = models.CharField(max_length=50, unique=True, validators=[validate_username])
    first_name   = None 
    last_name    = None


    def save(self, *args, **kwargs):
        self.email = self.email.lower()  
        super().save(*args, **kwargs)


    def __str__(self):
        return self.username