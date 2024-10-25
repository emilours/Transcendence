from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from frontend.models import Game, Match, PlayerMatch, CustomUser
import json, asyncio
from asgiref.sync import sync_to_async


@login_required
def pong(request):
	context = {}
	if request.user.is_authenticated:
		username = request.user.display_name
		avatar = request.user.avatar.url
		print(f"username: {username}, avatar: {avatar}")
		context = {
			'username': username,
			'avatar': avatar
		}
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('pong.html', context, request=request)
		return JsonResponse({'html': html, 'username': username, 'avatar': avatar})
	return render(request, 'base.html')


@csrf_exempt
def SaveLocalPongMatch(request):
	if request.method == 'POST':
		try:
			print('--------HERE--------')
			if request.user.is_authenticated:
				user = request.user
				print(f"[PONG LOG] type of user: {type(user)}")

			data = json.loads(request.body)

			score = data.get('score')
			game_name = 'pong'
			status = 'completed'
			description = 'pong local'

			print('user_id', user.id, 'score', score, 'game_name', game_name)

			if user and score is not None:
				game, _ = Game.objects.get_or_create(name=game_name, description=description)
				match = Match.objects.create(game=game, status=status, details=description)
				PlayerMatch.objects.create(player=user, match=match, score=score, is_winner=True)

				# TODO: Add score or remove to CustomUser
				return JsonResponse({'status': 'success'})
			return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
		except Exception as e:
			return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
	return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@sync_to_async
def session_close(user):
    user.active_sessions -= 1
    
    if user.active_sessions == 0:
        user.is_online = False

    user.save(update_fields=['active_sessions', 'is_online'])
    
    # return JsonResponse({"message": "Session closed, active sessions updated."}, status=200)

@sync_to_async
def session_open(user):
    user.active_sessions += 1
    user.is_online = True
    user.save(update_fields=['active_sessions', 'is_online'])
    
    # return JsonResponse({"message": "Session opened, active sessions updated."}, status=200)