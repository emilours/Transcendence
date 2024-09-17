import pytest
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.urls import reverse

@pytest.mark.django_db
def test_delete_profile_deletes_tokens(client):
    User = get_user_model()
    user = User.objects.create_user(display_name='testuser', email='testuser@example.com', password='password')
    token = Token.objects.create(user=user)
    
    client.force_login(user)
    
    url = reverse('authentification:delete_profile')
    response = client.post(url, HTTP_AUTHORIZATION=f'Token {token.key}')
    
    assert response.status_code == 200
    
    # le token a été supprimé
    assert not Token.objects.filter(key=token.key).exists()
    
    # l'utilisateur a été supprimé
    assert not User.objects.filter(id=user.id).exists()