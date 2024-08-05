from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
	username = forms.CharField(label='Email')
	password = forms.CharField(label='Password', widget=forms.PasswordInput)
