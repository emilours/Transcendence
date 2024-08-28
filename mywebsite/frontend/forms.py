from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'display_name', 'password1', 'password2', 'avatar')

# class CustomAuthenticationForm(AuthenticationForm):
# 	class Meta:
# 		model = CustomUser
# 		fields = ('email', 'password')
