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

    def test_signup_with_special_chars_lastname(self):
        response = self.client.post(self.signup_url, {
            'firstname': 'John',
            'lastname': 'D@e',
            'email': 'john.doe@example.com',
            'password1': 'PoulettePoulette159!!',
            'password2': 'PoulettePoulette159!!',
            'display_name': 'johnny',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "No special chars in last name field.")
    
        def test_signup_with_special_chars_firstname(self):
            response = self.client.post(self.signup_url, {
                'firstname': 'J!!!hn',
                'lastname': 'Doe',
                'email': 'john.doe@example.com',
                'password1': 'PoulettePoulette159!!',
                'password2': 'PoulettePoulette159!!',
                'display_name': 'johnny',
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['error'], "No special chars in first name field.")

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

    def test_signup_with_existing_username(self):
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
        self.assertEqual(response.json()['error'], "Username is already taken.")

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
# # ===                                                      SIGNOUT TEST                                                                                 ===
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
