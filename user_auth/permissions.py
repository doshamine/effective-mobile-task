from rest_framework.permissions import BasePermission
from rest_framework import exceptions

from user_auth.auth import get_sub
from user_auth.models import User


class TokenPermission(BasePermission):
    def has_permission(self, request, view):
        if 'Authorization' not in request.headers:
            raise exceptions.AuthenticationFailed('Authorization header is required')
        auth_header = request.headers['Authorization']

        if 'Bearer ' not in auth_header:
            raise exceptions.AuthenticationFailed('Incorrect header format')

        token = auth_header.replace('Bearer ', '')

        user = User.objects.get(id=get_sub(token))
        return bool(user and user.is_active)