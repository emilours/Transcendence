from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def home(request):
	return render(request, 'index.html')

def index(request):
	return render(request, 'index.html')

# def signup_view(request):
# 	if request.method == 'POST':
# 		form = CustomUserCreationForm(request.POST)
# 		if form.is_valid():
# 			user = form.save()
# 			login(request, user)
# 			return redirect('index')
# 	else:
# 		form = CustomUserCreationForm()
# 	return render(request, 'signup.html', {'form': form})

# def login_view(request):
# 	# Implémentez la logique de connexion ici
# 	return render(request, 'login.html')

# def login_view(request):
#     if request.method == 'POST':
#         form = CustomAuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('index')
#     else:
#         form = CustomAuthenticationForm()
#     return render(request, 'login.html', {'form': form})

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

