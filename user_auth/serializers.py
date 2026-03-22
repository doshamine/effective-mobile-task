from rest_framework import serializers

from user_auth.hash import hash_password
from user_auth.models import User, Role


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data.pop('role')
        role = Role.objects.get(name='user')

        password = validated_data.pop('password')
        hashed_password = hash_password(password)

        user = User(**validated_data, password=hashed_password, role=role)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            hashed_password = hash_password(password)
            instance.password = hashed_password

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance