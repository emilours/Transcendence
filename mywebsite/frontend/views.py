from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def home(request):
	return render(request, 'index.html')

def index(request):
	return render(request, 'index.html')
