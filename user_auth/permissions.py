from typing import List

from rest_framework.permissions import BasePermission
from effective_mobile_task import settings

paths = {
    "user": "users",
    "item": "items",
}

methods = {
    "create": "POST",
    "read": "GET",
    "update": "PATCH",
    "delete": "DELETE",
}


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
            operation = permission_parts[-1]

            if paths[obj] in path and methods[operation] == method:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        for permission in user.role.permissions.all():
            belongs = parse_permission(permission.name)[1]

            if belongs == "all":
                return True
            if belongs == "own":
                return obj.owner == user

        return False
