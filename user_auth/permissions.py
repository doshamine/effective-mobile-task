from typing import List

from jwt import InvalidTokenError
from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from rest_framework.request import Request

from effective_mobile_task import settings
from user_auth.auth import get_payload, extract_token, get_jti, get_sub, get_user
from user_auth.models import User, RefreshToken
from user_auth.token_types import TokenType

paths = {
    'user': 'users',
    'item': 'items',
}

methods = {
    'create': 'POST',
    'read': 'GET',
    'update': 'PATCH',
    'delete': 'DELETE',
}


def parse_permission(permission: str) -> List[str]:
    return permission.split(settings.PERMISSION_SEPARATOR)


class RefreshTokenPermission(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        refresh_token = request.data.get("refresh_token")

        is_login = RefreshToken.objects.filter(pk=get_jti(refresh_token)).exists()
        return is_login


class AccessTokenPermission(BasePermission):
    def has_permission(self, request, view):
        token = extract_token(request.headers)

        try:
            payload = get_payload(token)

            if payload.get('type') != TokenType.ACCESS.value:
                raise exceptions.AuthenticationFailed("Invalid token type")

        except InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user = User.objects.get(id=payload.get('sub'))
        return bool(user) and user.is_active


class RolePermission(BasePermission):
    def has_permission(self, request, view):
        access_token = extract_token(request.headers)
        user = get_user(access_token)

        path = request.path
        method = request.method
        for permission in user.role.permissions.all():
            permission_parts = parse_permission(permission.name)
            obj = permission_parts[0]
            operation = permission_parts[-1]

            if paths[obj] in path and methods[operation] == method:
                return True

        return False

