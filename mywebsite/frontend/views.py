from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index(request):
	redirect('home')

def home(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('home.html', request=request)
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
