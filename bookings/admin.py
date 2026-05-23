from django.contrib import admin
from bookings.models import Booking, WaitlistEntry


admin.site.register(Booking)
admin.site.register(WaitlistEntry)
