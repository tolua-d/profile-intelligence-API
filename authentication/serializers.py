from rest_framework import serializers
from authentication.models import User


class SignUserUpSerializer(serializers.Serializer):
    """Serializer for user signup"""
    email = serializers.EmailField()
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'github_username',
            'role', 'is_active', 'is_verified',
            'created_at', 'updated_at', 'last_login_at'
        )
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'last_login_at'
        )


class LoginUserSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh"""
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout"""
    refresh = serializers.CharField(required=False)
