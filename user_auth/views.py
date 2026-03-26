from datetime import timedelta

from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from effective_mobile_task import settings
from user_auth.auth import (
    generate_access_token,
    generate_refresh_token,
)
from user_auth.authentication import (
    AccessTokenAuthentication,
    RefreshTokenAuthentication,
)
from user_auth.hash import check_password
from user_auth.models import User, RefreshToken, Role, Permission
from user_auth.permissions import RolePermission, parse_permission
from user_auth.serializers import UserSerializer, RoleSerializer, PermissionSerializer, AuthSerializer


class BaseUserView(GenericAPIView):
    serializer_class = AuthSerializer

    def get_queryset(self):
        return User.objects.filter(is_active=True)


class RegisterUserView(BaseUserView, CreateModelMixin):
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UpdateUserView(BaseUserView, UpdateModelMixin):
    authentication_classes = (AccessTokenAuthentication,)

    def get_object(self) -> User:
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class DeleteUserView(BaseUserView, DestroyModelMixin):
    authentication_classes = (AccessTokenAuthentication,)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (RolePermission,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user

        if self.action == 'list' and self._has_own_only_permission(user):
            queryset = queryset.filter(id=user.id)
        return queryset

    def _has_own_only_permission(self, user: User) -> bool:
        permission = user.role.permissions.filter(name__contains='user:read').first()
        parts = parse_permission(permission.name)

        if len(parts) == 3 and parts[2] == 'own':
            return True
        return False


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        missing_fields = []
        if email is None:
            missing_fields.append("email")
        if password is None:
            missing_fields.append("password")

        if missing_fields:
            return Response(
                {
                    "detail": "Required fields are missing.",
                    "missing_fields": missing_fields,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check_password(password, user.password):
            return Response(
                {"detail": "Wrong password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"detail": "User account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        access_token = generate_access_token(
            str(user.id), timedelta(minutes=settings.JWT_ACCESS_MINUTES)
        )
        refresh_token = generate_refresh_token(
            str(user.id), timedelta(days=settings.JWT_REFRESH_DAYS)
        )

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    authentication_classes = (RefreshTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        access_token = generate_access_token(
            request.auth.get("sub"), timedelta(minutes=settings.JWT_ACCESS_MINUTES)
        )
        return Response({"access_token": access_token}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    authentication_classes = (AccessTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        RefreshToken.objects.filter(subject=request.auth.get("sub")).delete()
        return Response(status=status.HTTP_200_OK)


class RoleViewSet(ModelViewSet):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (RolePermission,)
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class PermissionViewSet(ModelViewSet):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (RolePermission,)
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer