from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SignUpForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
		widgets = {
			'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
			'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
			'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
			'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
			'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
		}

class LoginForm(AuthenticationForm):
	username = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from .models import CustomUser

# class CustomUserCreationForm(UserCreationForm):
# 	class Meta:
# 		model = CustomUser
# 		fields = ('email', 'first_name', 'last_name', 'display_name', 'password1', 'password2', 'avatar')

# class CustomAuthenticationForm(AuthenticationForm):
# 	class Meta:
# 		model = CustomUser
# 		fields = ('email', 'password')
