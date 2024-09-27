# # ================================================================================================================================================================
# # ===                                                      DELETE PROFILE TEST                                                                                 ===
# # ================================================================================================================================================================

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

# # ================================================================================================================================================================
# # ===                                                      SIGNUP TEST                                                                                 ===
# # ================================================================================================================================================================


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import tempfile

User = get_user_model()

class SignUpTest(TestCase):
    def setUp(self):
        self.signup_url = reverse('authentification:signup')

    def test_signup_with_missing_fields(self):
        response = self.client.post(self.signup_url, {
            'firstname': 'John',
            # Last name is missing
            'email': 'john.doe@example.com',
            'password1': 'PoulettePoulette159!!',
            'password2': 'PoulettePoulette159!!',
            'display_name': 'johnny',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "All fields are required.")

    # def test_signup_with_special_chars_lastname(self):
    #     response = self.client.post(self.signup_url, {
    #         'firstname': 'John',
    #         'lastname': 'D@e',
    #         'email': 'john.doe@example.com',
    #         'password1': 'PoulettePoulette159!!',
    #         'password2': 'PoulettePoulette159!!',
    #         'display_name': 'johnny',
    #     })
    #     self.assertEqual(response.status_code, 400)
    #     response_data = response.json()
    #     self.assertEqual(response_data['error'], "No special chars in last name field.")
    
    # def test_signup_with_special_chars_firstname(self):
    #     response = self.client.post(self.signup_url, {
    #         'firstname': 'J!!!hn',
    #         'lastname': 'Doe',
    #         'email': 'john.doe@example.com',
    #         'password1': 'PoulettePoulette159!!',
    #         'password2': 'PoulettePoulette159!!',
    #         'display_name': 'johnny',
    #     })
    #     self.assertEqual(response.status_code, 400)
    #     response_data = response.json()
    #     self.assertEqual(response_data['error'], "['Error: this field can only contain letters and spaces.']")

    def test_signup_with_mismatched_passwords(self):
        response = self.client.post(self.signup_url, {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'PoulettePoulette159!!',
            'password2': 'PoulettePoulette179!!',
            'display_name': 'johnny',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Passwords do not match.")

    def test_signup_with_existing_email(self):
        User.objects.create_user(email='john.doe@example.com', password='password123')
        
        response = self.client.post(self.signup_url, {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'PoulettePoulette159!!',
            'password2': 'PoulettePoulette159!!',
            'display_name': 'johnny',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "Email is already in use.")

    def test_signup_with_existing_display_name(self):
        User.objects.create_user(email='another.email@example.com', password='password123', display_name='johnny')

        response = self.client.post(self.signup_url, {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'PoulettePoulette159!!',
            'password2': 'PoulettePoulette159!!',
            'display_name': 'johnny',
        })
        self.assertEqual(response.status_code, 400)
    
        # Utilisez .json() au lieu de .data pour accéder à la réponse JSON
        response_data = response.json()
        self.assertEqual(response_data['error'], "Username is already taken.")

    def test_signup_with_large_avatar(self):
        large_avatar = tempfile.NamedTemporaryFile(suffix=".png")
        large_avatar.write(b"x" * (2 * 1024 * 1024 + 1))  # Fichier de plus de 2MB
        large_avatar.seek(0)
        
        response = self.client.post(self.signup_url, {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'PoulettePoulette159!!',
            'password2': 'PoulettePoulette159!!',
            'display_name': 'johnny',
            'avatar': large_avatar,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "File size exceeds the maximum limit of 2MB.")

    def test_signup_success(self):
        response = self.client.post(self.signup_url, {
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john.doe@example.com',
            'password1': 'PoulettePoulette159!!',
            'password2': 'PoulettePoulette159!!',
            'display_name': 'johnny',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], "Account successfully created and logged in.")

        user = User.objects.filter(email='john.doe@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.display_name, 'johnny')

# # ================================================================================================================================================================
# # ===                                                      SIGNOUT TEST                                                                                        ===
# # ================================================================================================================================================================

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import logout
from rest_framework.test import APIClient
from rest_framework import status

class SignoutTest(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='securepassword',
            display_name='TestUser'
        )
        self.url = reverse('authentification:signout')

    def test_signout_success(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "You have successfully logged out.")

    def test_signout_after_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "You have successfully logged out.")
        self.assertTrue(self.client.session.is_empty())

    # def test_signout_api(self):
    #     api_client = APIClient()
    #     api_client.force_authenticate(user=self.user)
        
    #     response = api_client.post(self.url)
        
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json()['message'], "You have successfully logged out.")
        
    #     invalid_response = api_client.get('/api/some-endpoint/')
    #     self.assertEqual(invalid_response.status_code, 401)
    #     self.assertIn("Authentication credentials were not provided.", str(invalid_response.content))
    
    def test_signout_session_flush(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "You have successfully logged out.")
        self.assertTrue(self.client.session.is_empty())

# # ================================================================================================================================================================
# # ===                                                      CHECK FRIEND STATUS TEST                                                                            ===
# # ================================================================================================================================================================

import pytest
from unittest.mock import MagicMock
from django.contrib.auth import get_user_model
from frontend.models import FriendRequest

User = get_user_model()

@pytest.mark.django_db
def test_check_friend_request_status():
    user = User.objects.create(display_name="testuser", email="testuser@example.com")
    user2 = User.objects.create(display_name="user2", email="user2@example.com")
    user3 = User.objects.create(display_name="user3", email="user3@example.com")

    friend_request1 = FriendRequest.objects.create(sender=user, receiver=user2, status="accepted")
    friend_request2 = FriendRequest.objects.create(sender=user, receiver=user3, status="declined")

    request = MagicMock()
    request.user = user

    result = check_friend_request_status(request.user)

    assert len(result) == 2
    assert result[0]["id"] == friend_request1.id
    assert result[1]["id"] == friend_request2.id
    assert result[0]["status"] == "accepted"
    assert result[1]["status"] == "declined"

    FriendRequest.objects.all().delete()
    result = check_friend_request_status(request.user)
    assert result == []


# # ================================================================================================================================================================
# # ===                                                      CHECK SSE VIEW TEST                                                                                 ===
# # ================================================================================================================================================================

import pytest
import json
from unittest.mock import patch
from django.http import StreamingHttpResponse
from django.test import RequestFactory
from frontend.models import FriendRequest, CustomUser
from .views import sse, check_friend_request_status

@pytest.mark.django_db
@patch('time.sleep', return_value=None)
def test_sse_view(mock_sleep):
    user = CustomUser.objects.create(display_name="testuser", email="testuser@example.com")
    user2 = CustomUser.objects.create(display_name="user2", email="user2@example.com")
    user3 = CustomUser.objects.create(display_name="user3", email="user3@example.com")

    FriendRequest.objects.create(
        sender=user, receiver=user2, status="accepted"
    )

    factory = RequestFactory()
    request = factory.get('/sse')
    
    request.user = user

    response = sse(request)
    assert isinstance(response, StreamingHttpResponse)
    assert response['Content-Type'] == 'text/event-stream'

    event_generator = response.streaming_content
    first_event = next(event_generator)
    first_data = first_event.decode('utf-8')

    assert "data:" in first_data
    status_update = json.loads(first_data.split("data: ")[1])
    assert len(status_update) == 1
    assert status_update[0]["status"] == "accepted"

    FriendRequest.objects.create(
        sender=user, receiver=user3, status="declined"
    )

    second_event = next(event_generator)
    second_data = second_event.decode('utf-8')
    status_update = json.loads(second_data.split("data: ")[1])
    assert len(status_update) == 2
    assert status_update[1]["status"] == "declined"
