from django.db.models import Prefetch
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from frontend.models import Game, Match, PlayerMatch
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
import json

@login_required
def invaders(request):
	context = {}
	if request.user.is_authenticated:
		test_name = request.user.display_name
		context = {
			'test_name': test_name
		}
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('invaders.html', context, request=request)
		return JsonResponse({'html': html, 'test_name': test_name})
	return render(request, 'base.html')


@csrf_exempt
def save_match(request):
	if request.method == 'POST':
		try:
			print('--------HERE--------')
			if request.user.is_authenticated:
				user = request.user

			data = json.loads(request.body)

			score = data.get('score')
			game_name = 'Invaders'
			status = 'completed'
			description = 'Arcade game'

			print('user_id', user.id, 'score', score, 'game_name', game_name)

			if user and score is not None:
				game, _ = Game.objects.get_or_create(name=game_name, description=description)
				match = Match.objects.create(game=game, status=status, details=description)
				PlayerMatch.objects.create(player=user, match=match, score=score, is_winner=True)

				return JsonResponse({'status': 'success'})
			return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
		except Exception as e:
			return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
	return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def invader_leaderboard(request):
	leaderboard_data = []
	print('+++++++++++++++++AQUI')

	invader_game = Game.objects.filter(name='Invaders').first()
	if invader_game:
		matches = Match.objects.filter(game=invader_game).prefetch_related(
			Prefetch('playermatch_set', queryset=PlayerMatch.objects.select_related('player'))
		)

		for match in matches:
			for player_match in match.playermatch_set.all():
				leaderboard_data.append({
					'score': player_match.score,
					'display_name': player_match.player.display_name,
					'date': match.date.strftime('%Y-%m-%d'),
					'game': match.details,
				})
				print('score', player_match.score)
				print('display_name', player_match.player.display_name)
				print('date', match.date.strftime('%Y-%m-%d'))
				print('game', match.details)

	return JsonResponse(leaderboard_data, safe=False)
