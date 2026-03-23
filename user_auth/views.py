import jwt
from jwt import InvalidTokenError
from rest_framework import viewsets, status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from effective_mobile_task import settings
from user_auth.hash import check_password
from user_auth.models import User
from user_auth.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


def check_token(request):
    if 'Authorization' not in request.headers:
        raise exceptions.AuthenticationFailed('Authorization header is required')

    auth_header = request.headers['Authorization']

    if 'Bearer ' not in auth_header:
        raise exceptions.AuthenticationFailed('Incorrect header format')

    token = auth_header.replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except InvalidTokenError:
        raise exceptions.AuthenticationFailed('Invalid token')

    user = User.objects.get(id=payload['sub'])
    if not user or not user.is_active:
        raise exceptions.AuthenticationFailed('No such user')


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        user = User.objects.get(email=request.data['email'])

        if not check_password(request.data['password'], user.password):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response(status=status.HTTP_403_FORBIDDEN)

        token = jwt.encode(payload={'sub': user.id}, key=settings.SECRET_KEY, algorithm='HS256')

        return Response({
            'token': token
        }, status=status.HTTP_200_OK)

