from rest_framework import serializers

from mock.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
            "id",
            "name",
            "owner",
        )
        read_only_fields = (
            "id",
            "owner",
        )
