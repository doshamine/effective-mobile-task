from jwt import InvalidTokenError, DecodeError
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from user_auth.auth import get_jti, extract_token, get_payload
from user_auth.models import RefreshToken, User
from user_auth.token_types import TokenType


class BaseTokenAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        return "Bearer"


class AccessTokenAuthentication(BaseTokenAuthentication):
    def authenticate(self, request):
        token = extract_token(request.headers)
        if not token:
            raise exceptions.AuthenticationFailed("Authorization token is not provided.")

        try:
            payload = get_payload(token)
        except InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token.")

        token_type = payload.get("type")
        if token_type != TokenType.ACCESS.value:
            raise exceptions.AuthenticationFailed("Invalid token type.")

        user_id = payload.get("sub")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found.")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User account is inactive.")

        return user, payload


class RefreshTokenAuthentication(BaseTokenAuthentication):
    def authenticate(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            raise exceptions.AuthenticationFailed(
                "Refresh token is not provided."
            )

        try:
            jti = get_jti(refresh_token)
        except DecodeError:
            raise exceptions.AuthenticationFailed(
                "Invalid refresh token."
            )

        try:
            refresh_token_obj = RefreshToken.objects.get(jti=jti)
        except RefreshToken.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "Refresh token not found."
            )

        user = getattr(refresh_token_obj, "subject", None)
        if user is None:
            raise exceptions.AuthenticationFailed(
                "User associated with this token was not found."
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                "User account is inactive."
            )

        payload = get_payload(refresh_token)

        return user, payload
