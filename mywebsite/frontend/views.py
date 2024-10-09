from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Max, Avg
from .models import PlayerMatch, CustomUser

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

def error_api(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('error_api.html', request=request)
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

def games(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('games.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

def leaderboard(request):
	leaderboard_data = PlayerMatch.objects.select_related('player', 'match').order_by('-score')

	pong_leaderboard = []
	invaders_leaderboard = []

	pong_rank = 1
	invaders_rank = 1

	for entry in leaderboard_data:
		if entry.match.game.name == "Pong":
			pong_leaderboard.append((pong_rank, entry))
			pong_rank += 1
		if pong_rank > 5:
			break

	for entry in leaderboard_data:
		if entry.match.game.name == "Invaders":
			invaders_leaderboard.append((invaders_rank, entry))
			invaders_rank += 1
		if invaders_rank > 5:
			break

	context = {
		'pong_leaderboard': pong_leaderboard,
		'invaders_leaderboard': invaders_leaderboard,
	}

	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('leaderboard.html', context, request=request)
		return JsonResponse({'html': html})

	return render(request, 'base.html', context)

def user_dashboard(request, username):
	user = get_object_or_404(CustomUser, display_name=username)
	dashboard_data = PlayerMatch.objects.select_related('player', 'match').filter(player__display_name=user.display_name).order_by('-match__date')

	pong_stats = {
		'total_matches': dashboard_data.filter(match__game__name="Pong").count(),
		'victories': dashboard_data.filter(match__game__name="Pong", is_winner=True).count(),
		'defeats': dashboard_data.filter(match__game__name="Pong", is_winner=False).count(),
		'max_score': dashboard_data.filter(match__game__name="Pong").aggregate(Max('score'))['score__max']
	}

	invaders_stats = {
		'total_matches': dashboard_data.filter(match__game__name="Invaders").count(),
		'average': dashboard_data.filter(match__game__name="Invaders").aggregate(Avg('score'))['score__avg'],
		'max_score': dashboard_data.filter(match__game__name="Invaders").aggregate(Max('score'))['score__max']
	}

	context = {
		'user_profile': user,
		'pong_stats': pong_stats,
		'invaders_stats': invaders_stats,
		'dashboard_data': dashboard_data,
	}

	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('dashboard.html', context, request=request)
		return JsonResponse({'html': html})

	return render(request, 'base.html', context)

def load_header(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('header.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

