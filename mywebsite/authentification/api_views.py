from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth.models import User
from frontend.models import CustomUser
from .serializers import AuthorizationCodeSerializer
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from urllib.parse import urlparse
from django.contrib.auth import login
import requests
import os

@api_view(['GET'])
@permission_classes([AllowAny])
def callback_42(request):
    token_url = settings.FORTYTWO_TOKEN_URL
    serializer = AuthorizationCodeSerializer(data=request.GET)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    code = serializer.validated_data.get('code')
    if not code:
        return Response({'error': 'Code not provided'}, status=400)
    
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': settings.FORTYTWO_CLIENT_ID,
        'client_secret': settings.FORTYTWO_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.FORTYTWO_REDIRECT_URI,
    }
    
    token_response = requests.post(token_url, data=token_data)
    
    if token_response.status_code != 200:
        return Response({'error': 'Failed to obtain access token'}, status=token_response.status_code)
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        return Response({'error': 'Access token not provided'}, status=400)
    
    user_info_response = requests.get(settings.FORTYTWO_USER_URL, headers={
        'Authorization': f'Bearer {access_token}'
    })
    
    if user_info_response.status_code != 200:
        return Response({'error': 'Failed to obtain user info'}, status=user_info_response.status_code)
    
    user_info = user_info_response.json()

    email = user_info.get('email')
    display_name = user_info.get('login')
    first_name = user_info.get('first_name')
    last_name = user_info.get('last_name')

    avatar_url = user_info.get('image', {}).get('link')
    
    if not email or not display_name:
        return Response({'error': 'Incomplete user info'}, status=400)
    
    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={
            'display_name': display_name,
            'first_name': first_name,
            'last_name': last_name
        }
    )
     
    if not created:
        user.first_name = first_name
        user.last_name = last_name
    
    if avatar_url:
        avatar_response = requests.get(avatar_url)
        if avatar_response.status_code == 200:
            avatar_name = os.path.basename(urlparse(avatar_url).path)
            avatar_content = ContentFile(avatar_response.content)
            user.avatar.save(avatar_name, avatar_content, save=False)
        else:
            return Response({'error': f'Failed to download avatar from {avatar_url}. Status code: {avatar_response.status_code}'}, status=avatar_response.status_code)

    user.save()

    login(request, user)
    user.is_online = True
    user.save(update_fields=['is_online'])
    return redirect('/profile/')

    # refresh = RefreshToken.for_user(user)
    
    # return Response({
        # 'refresh': str(refresh),
        # 'access': str(refresh.access_token),
    # })

    # Usage approprié : AllowAny est approprié ici parce que l'endpoint doit
    # permettre à des utilisateurs non authentifiés de se connecter ou de
    # s'enregistrer. C'est le point d'entrée pour obtenir un token d'accès,
    # ce qui nécessite que les utilisateurs puissent accéder à cet endpoint
    # sans être authentifiés au préalable.


# # ================================================================================================================================================================
# # ===                                                      DELETE USER ACCOUNT                                                                                ===
# # ================================================================================================================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_profile_api(request):
    try:
        user = request.user
        user.delete()

        return Response({
            'message': 'Profile and all associated data successfully deleted.'
        }, status=200)

    except IntegrityError as e:
        return Response({
            'error': 'An error occurred while deleting the profile.',
            'details': str(e)
        }, status=400)
    except Exception as e:
        return Response({
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }, status=400)