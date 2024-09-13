from rest_framework import serializers
from frontend.models import CustomUser

class AuthorizationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=255)

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'display_name', 'first_name', 'last_name']