from rest_framework import serializers

from user_auth.hash import hash_password
from user_auth.models import User, Role, Permission


def process_password(validated_data):
    validated_data.pop("password_confirm")

    if "password" in validated_data:
        password = validated_data.pop("password")
        validated_data["password"] = hash_password(password)

    return validated_data


class AuthSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
            "created_at"
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password:
            if not password_confirm:
                raise serializers.ValidationError(
                    {"password_confirm": "Password confirmation required"}
                )
            if password != password_confirm:
                raise serializers.ValidationError(
                    {"password_confirm": "Passwords do not match"}
                )

        return attrs

    def create(self, validated_data):
        validated_data = process_password(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = process_password(validated_data)
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "created_at",
            "role"
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "password": {"write_only": True},
        }


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(many=True, queryset=Permission.objects.all())

    class Meta:
        model = Role
        fields = ("id", "name", "display_name", "description", "permissions")
