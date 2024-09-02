from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth.models import User
from frontend.models import CustomUser
import requests

@api_view(['GET'])
@permission_classes([AllowAny])
def callback_42(request):
    token_url = settings.FORTYTWO_TOKEN_URL
    code = request.GET.get('code')
    if not code:
        return Response({'error': 'Code not provided'}, status=400)
    
    # Échange du code contre un jeton d'accès
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': settings.FORTYTWO_CLIENT_ID,
        'client_secret': settings.FORTYTWO_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.FORTYTWO_REDIRECT_URI,
    }
    
    token_response = requests.post(settings.FORTYTWO_TOKEN_URL, data=token_data)
    
    if token_response.status_code != 200:
        return Response({'error': 'Failed to obtain access token'}, status=token_response.status_code)
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        return Response({'error': 'Access token not provided'}, status=400)
    
    # Récupération des informations utilisateur
    user_info_response = requests.get(settings.FORTYTWO_USER_URL, headers={
        'Authorization': f'Bearer {access_token}'
    })
    
    if user_info_response.status_code != 200:
        return Response({'error': 'Failed to obtain user info'}, status=user_info_response.status_code)
    
    user_info = user_info_response.json()

    # Création ou récupération de l'utilisateur Django
    email = user_info.get('email')
    display_name = user_info.get('login')
    
    if not email or not display_name:
        return Response({'error': 'Incomplete user info'}, status=400)
    
    user, created = CustomUser.objects.get_or_create(email=email, defaults={'display_name': display_name})
    
    # Générer un JWT pour l'utilisateur
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })
