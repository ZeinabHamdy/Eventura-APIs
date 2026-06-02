from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


from .models import User
from .permissions import IsAdminUser
from utils.mixins import PaginatedActionMixin
from .serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    AdminUserSerializer,
)


class AuthViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response({
                'message': 'Account created successfully.',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            token = RefreshToken(request.data['refresh']) # take refresh token from request
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response(
                {'error': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST
            )




class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        # update in profile
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password']) # type: ignore
            request.user.save()
            return Response({'message': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='delete-account')
    def delete_account(self, request):
        request.user.delete()
        return Response(
            {'message': 'Account deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )


class AdminViewSet(PaginatedActionMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends    = [DjangoFilterBackend, SearchFilter]
    filterset_fields   = ['is_superuser', 'is_active']
    search_fields      = ['name', 'email']
    serializer_class   = AdminUserSerializer

    @action(detail=False, methods=['get'])
    def users(self, request):
        queryset = User.objects.all()
        queryset = self.filter_queryset(queryset)
        return self.paginated_response(queryset, AdminUserSerializer)