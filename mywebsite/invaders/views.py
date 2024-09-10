from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from frontend.models import Game, Match, PlayerMatch

def invaders(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('invaders.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

# def invaders(request):
# 	return render(request, 'invaders.html')

# def invaders(request):
#     try:
#         game = Game.objects.get(name='Pusheen Invaders')
#     except Game.DoesNotExist:
#         return JsonResponse({'error': 'Game not found'}, status=404)

#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':

#         matches = Match.objects.filter(game=game).order_by('-date')[:3]
        
#         match_data = []
#         for match in matches:
#             player_matches = PlayerMatch.objects.filter(match=match)
#             players = [
#                 {
#                     'display_name': player_match.player.display_name,
#                     'score': player_match.score,
#                     'is_winner': player_match.is_winner
#                 }
#                 for player_match in player_matches
#             ]
#             match_data.append({
#                 'date': match.date,
#                 'details': match.details,
#                 'status': match.status,
#                 'players': players
#             })

#         html = render_to_string('invaders.html', {'matches': match_data}, request=request)
#         return JsonResponse({'html': html})

#     return render(request, 'base.html')
