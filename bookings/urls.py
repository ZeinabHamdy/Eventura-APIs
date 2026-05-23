from rest_framework.routers import DefaultRouter
from bookings.views import BookingViewSet, WaitlistViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'waitlist', WaitlistViewSet, basename='waitlist')

urlpatterns = router.urls