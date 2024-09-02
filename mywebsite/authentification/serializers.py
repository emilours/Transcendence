from rest_framework import serializers

class AuthorizationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=255)