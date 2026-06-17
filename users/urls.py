from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema

from .views import AuthViewSet, UserViewSet
from .serializers import CustomTokenObtainPairSerializer

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register('users', UserViewSet, basename='users')


@extend_schema(
    tags=['1. Auth'],
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=['1. Auth'],
)
class CustomTokenRefreshView(TokenRefreshView):
    pass

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(permission_classes=[AllowAny]), name='login'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('', include(router.urls)),
]