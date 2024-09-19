from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

def index(request):
	redirect('home')

def home(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('home.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def login(request):
	context = {
		'api_42_auth_url': settings.API_42_AUTH_URL
	}
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('login.html', context, request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def signup(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('signup.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def contact(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('contact.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def deleted_profile(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('deleted_profile.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

@login_required
def profile(request):
	pending_requests = request.user.get_pending_friend_requests()
	sent_requests = request.user.get_sent_friend_requests()
	context = {
		'pending_requests': pending_requests,
		'sent_requests': sent_requests
	}
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('profile.html', context, request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

@login_required
def edit_profile(request):
	predefined_avatars = [
		{"url": "../media/img/avatars/avatar0.jpg"},
		{"url": "../media/img/avatars/avatar1.jpg"},
		{"url": "../media/img/avatars/avatar2.jpg"},
		{"url": "../media/img/avatars/avatar3.jpg"},
		{"url": "../media/img/avatars/avatar4.jpg"},
		{"url": "../media/img/avatars/avatar5.jpg"},
		{"url": "../media/img/avatars/avatar6.jpg"},
	]

	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('edit_profile.html', {'predefined_avatars': predefined_avatars}, request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html', {'predefined_avatars': predefined_avatars})

@login_required
def edit_password(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('edit_password.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

@login_required
def games(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('games.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

@login_required
def leaderboard(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('leaderboard.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def load_header(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('header.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')
