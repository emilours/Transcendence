from rest_framework import serializers
from frontend.models import CustomUser
from urllib.parse import urlparse
from django.core.files.base import ContentFile
import random
import string
import requests
import os

class AuthorizationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=255)

class CustomUserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'display_name', 'first_name', 'last_name', 'avatar']

    def validate_email(self, value):
        email = CustomUser.objects.normalize_email(value)

        user_id = self.instance.id if self.instance else None
        if CustomUser.objects.filter(email=email).exclude(id=user_id).exists():
            raise serializers.ValidationError("Email already in use.")

        return email

    def validate_display_name(self, value):
        user_id = self.instance.id if self.instance else None
        if CustomUser.objects.filter(display_name=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Username already in use.")

        return value

    def update(self, instance, validated_data):
        avatar_url = self.context.get('avatar_url')
        if avatar_url:
            avatar_response = requests.get(avatar_url, verify=False)
            if avatar_response.status_code == 200:
                avatar_name = os.path.basename(urlparse(avatar_url).path)
                instance.avatar.save(avatar_name, ContentFile(avatar_response.content), save=False)
            else:
                raise serializers.ValidationError(f"Failed to download avatar from {avatar_url}. Status code: {avatar_response.status_code}")

        return super().update(instance, validated_data)
