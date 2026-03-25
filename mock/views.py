from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from mock.constants import MOCK_DATA
from user_auth.permissions import AccessTokenPermission


class MockView(GenericViewSet):
    permission_classes = (AccessTokenPermission,)

    def create(self, request, *args, **kwargs):
        return Response(MOCK_DATA["CREATED"], status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        return Response(MOCK_DATA["OBJECT"], status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        return Response(MOCK_DATA["LIST"], status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        return Response(MOCK_DATA["MODIFIED"], status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        return Response(MOCK_DATA["SUCCESS"], status=status.HTTP_204_NO_CONTENT)
