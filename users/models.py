from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name         = models.CharField(max_length=50)
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_admin     = models.BooleanField(default=False)
    first_name   = None 
    last_name    = None

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username