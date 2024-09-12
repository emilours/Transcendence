from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.views.decorators.csrf import csrf_exempt
from frontend.models import Game, Match, PlayerMatch
from django.contrib.auth import get_user_model
import json

def invaders(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('invaders.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

@csrf_exempt
def save_arcade_score(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		user_id = data.get('user_id')
		score = data.get('score')
		game_name = data.get('game_name', 'Invaders Arcade')

		if user_id and score is not None:
			user = get_user_model().objects.get(id=user_id)
			game, _ = Game.objects.get_or_create(name=game_name, defaults={'description': 'Arcade game'})
			match = Match.objects.create(game=game, status='completed')
			PlayerMatch.objects.create(player=user, match=match, score=score, is_winner=True)

			return JsonResponse({'status': 'success'})
		return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
	return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
