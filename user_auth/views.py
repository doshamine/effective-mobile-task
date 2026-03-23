from datetime import timedelta

import jwt
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from effective_mobile_task import settings
from user_auth.auth import generate_access_token, generate_refresh_token
from user_auth.hash import check_password
from user_auth.models import User
from user_auth.permissions import TokenPermission
from user_auth.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [TokenPermission]

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        user = User.objects.get(email=request.data['email'])

        if not check_password(request.data['password'], user.password):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response(status=status.HTTP_403_FORBIDDEN)

        access_token = generate_access_token(str(user.id), timedelta(minutes=settings.JWT_ACCESS_MINUTES))
        refresh_token = generate_refresh_token(str(user.id), timedelta(days=settings.JWT_REFRESH_DAYS))

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token
        }, status=status.HTTP_200_OK)

