from jwt import InvalidTokenError
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from user_auth.auth import get_jti, extract_token, get_payload
from user_auth.models import RefreshToken, User
from user_auth.token_types import TokenType


class AccessTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = extract_token(request.headers)

        try:
            payload = get_payload(token)

            if payload.get("type") != TokenType.ACCESS.value:
                raise exceptions.AuthenticationFailed("Invalid token type")

        except InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user = User.objects.get(id=payload.get("sub"))
        return user, payload


class RefreshTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        refresh_token = request.data.get("refresh_token")
        refresh_token_obj = RefreshToken.objects.get(jti=get_jti(refresh_token))
        user = refresh_token_obj.subject
        return user, get_payload(refresh_token)
