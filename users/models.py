from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import UserManager
from users.validators import (
    validate_phone_number,
)


class User(AbstractUser):
    name         = models.CharField(max_length=50, null=True, blank=True)
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=13, unique=True, validators=[validate_phone_number], null=True, blank=True)
    first_name   = None 
    last_name    = None
    username     = None

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    objects: UserManager = UserManager()

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.email