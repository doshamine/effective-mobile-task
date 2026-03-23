from datetime import timezone, datetime

from jwt import InvalidTokenError
from rest_framework.permissions import BasePermission
from rest_framework import exceptions

from user_auth.auth import get_payload
from user_auth.models import User
from user_auth.token_types import TokenType


class TokenPermission(BasePermission):
    def has_permission(self, request, view):
        if "Authorization" not in request.headers:
            raise exceptions.AuthenticationFailed("Authorization header is required")
        auth_header = request.headers["Authorization"]

        if "Bearer " not in auth_header:
            raise exceptions.AuthenticationFailed("Incorrect header format")

        token = auth_header.replace("Bearer ", "")
        try:
            payload = get_payload(token)

            if payload["type"] != TokenType.ACCESS.value:
                raise exceptions.AuthenticationFailed("Invalid token type")

        except InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user = User.objects.get(id=payload["sub"])
        return bool(user and user.is_active)
