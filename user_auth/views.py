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
from user_auth.models import User, RefreshToken
from user_auth.permissions import RolePermission
from user_auth.serializers import UserSerializer


class BaseUserView(GenericAPIView):
    serializer_class = UserSerializer

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
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (RolePermission,)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        user = User.objects.get(email=request.data["email"])

        if not check_password(request.data["password"], user.password):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response(status=status.HTTP_403_FORBIDDEN)

        access_token = generate_access_token(
            str(user.id), timedelta(minutes=settings.JWT_ACCESS_MINUTES)
        )
        refresh_token = generate_refresh_token(
            str(user.id), timedelta(days=settings.JWT_REFRESH_DAYS)
        )

        return Response(
            {"access_token": access_token, "refresh_token": refresh_token},
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
