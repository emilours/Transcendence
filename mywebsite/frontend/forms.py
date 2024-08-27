from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'display_name', 'password1', 'password2', 'avatar')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password')

class UserUpdateForm(UserChangeForm):
    password = None
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'display_name', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and email != self.instance.email:
            if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('This email address is already in use.')
        return email

    def clean_display_name(self):
        display_name = self.cleaned_data.get('display_name')
        if display_name and display_name != self.instance.display_name:
            if CustomUser.objects.filter(display_name=display_name).exclude(pk=self.instance.pk).exists():
                raise ValidationError('This display name is already in use.')
        return display_name
