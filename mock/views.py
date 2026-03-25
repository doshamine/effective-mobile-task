from rest_framework.viewsets import ModelViewSet

from mock.models import Item
from mock.serializers import ItemSerializer
from user_auth.authentication import AccessTokenAuthentication
from user_auth.permissions import RolePermission


class MockView(ModelViewSet):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (RolePermission,)
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
