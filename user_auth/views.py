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
    get_payload,
    get_user,
    extract_token, get_sub,
)
from user_auth.hash import check_password
from user_auth.models import User, RefreshToken
from user_auth.permissions import AccessTokenPermission, RefreshTokenPermission, RolePermission
from user_auth.serializers import UserSerializer


class BaseUserView(GenericAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(is_active=True)


class RegisterUserView(BaseUserView, CreateModelMixin):
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UpdateUserView(BaseUserView, UpdateModelMixin):
    permission_classes = (AccessTokenPermission,)

    def get_object(self) -> User:
        token = extract_token(self.request.headers)
        return get_user(token)

    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class DeleteUserView(BaseUserView, DestroyModelMixin):
    permission_classes = (AccessTokenPermission,)

    def get_object(self) -> User:
        token = extract_token(self.request.headers)
        return get_user(token)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = (AccessTokenPermission, RolePermission, )


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
    permission_classes = (RefreshTokenPermission,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")

        access_token = generate_access_token(
            get_sub(refresh_token), timedelta(minutes=settings.JWT_ACCESS_MINUTES)
        )

        return Response({"access_token": access_token}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = (AccessTokenPermission,)

    def post(self, request, *args, **kwargs):
        access_token = extract_token(request.headers)
        payload = get_payload(access_token)
        RefreshToken.objects.filter(subject=payload.get('sub')).delete()

        return Response(status=status.HTTP_200_OK)
