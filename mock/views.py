from rest_framework.viewsets import ModelViewSet

from mock.models import Item
from mock.serializers import ItemSerializer
from user_auth.authentication import AccessTokenAuthentication
from user_auth.models import User
from user_auth.permissions import RolePermission, parse_permission


class MockView(ModelViewSet):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (RolePermission,)
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user

        if self.action == 'list' and self._has_own_only_permission(user):
            queryset = queryset.filter(owner=user)
        return queryset

    def _has_own_only_permission(self, user: User) -> bool:
        permission = user.role.permissions.filter(name__contains='item:read').first()
        parts = parse_permission(permission.name)

        if len(parts) >= 3 and parts[2] == 'own':
            return True
        return False

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
