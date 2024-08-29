from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
# from .forms import LoginForm, SignUpForm

def index(request):
	redirect('home')

def home(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('home.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def games(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('games.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')


def login(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('login.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def signup(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('signup.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

# def logout(request):
# 	return redirect('home')

def logout(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('logout.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def profile(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('profile.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def leaderboard(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('leaderboard.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')
