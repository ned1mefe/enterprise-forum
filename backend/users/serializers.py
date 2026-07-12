"""
User serializers for authentication and profile management.
"""

from rest_framework import serializers

from .models import User, UserRole


class LoginSerializer(serializers.Serializer):
    """Serializer for login request validation."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data.

    Used in profile endpoint and user management (admin).
    Password is write-only and never returned in responses.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users (admin only).

    Handles password hashing via create_user().
    """

    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Use create_user to properly hash the password."""
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
