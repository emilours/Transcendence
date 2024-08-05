from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout as auth_logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def home(request):
	return render(request, 'index.html')

def signup(request):
	return render(request, 'index.html')
# def signup(request):
# 	if request.method == 'POST':
# 		form = CustomUserCreationForm(request.POST)
# 		if form.is_valid():
# 			form.save()
# 			return redirect('login')
# 	else:
# 		form = CustomUserCreationForm()
# 	return render(request, 'signup.html', {'form': form})

# def login(request):
# 	if request.method == 'POST':
# 		form = CustomAuthenticationForm(data=request.POST)
# 		if form.is_valid():
# 			user = form.get_user()
# 			auth_login(request, user)
# 			return redirect('home')
# 	else:
# 		form = CustomAuthenticationForm()
# 	return render(request, 'login.html', {'form': form})

# def logout(request):
# 	auth_logout(request)
# 	return redirect('home')


