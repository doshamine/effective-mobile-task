from typing import List

from rest_framework.permissions import BasePermission
from effective_mobile_task import settings
from user_auth.mappings import PATHS, METHODS
from user_auth.models import User


def parse_permission(permission: str) -> List[str]:
    return permission.split(settings.PERMISSION_SEPARATOR)


class RolePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        path = request.path
        method = request.method

        for permission in user.role.permissions.all():
            permission_parts = parse_permission(permission.name)
            obj = permission_parts[0]
            operation = permission_parts[1]

            if PATHS[obj] in path and METHODS[operation] == method:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        for permission in user.role.permissions.all():
            permission_parts = parse_permission(permission.name)
            if len(permission_parts) < 3:
                return True
            elif isinstance(obj, User):
                return obj.id == user.id
            else:
                return obj.owner == user

        return False
