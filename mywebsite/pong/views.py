from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
# def pong(request):
# 	liveGames = 0
# 	gameId = liveGames
# 	liveGames += 1
# 	return render(request, 'pong/pong_home.html', {'gameId': gameId})

# def lobby(request, id):
# 	print(id)

# 	return render(request, 'pong/pong.html')

@login_required
def pong(request):
	context = {}
	if request.user.is_authenticated:
		test_name = request.user.display_name
		context = {
			'test_name': test_name
		}
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('pong.html', context, request=request)
		return JsonResponse({'html': html, 'test_name': test_name})
	return render(request, 'base.html')
