from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse

# Create your views here.
# def pong(request):
# 	liveGames = 0
# 	gameId = liveGames
# 	liveGames += 1
# 	return render(request, 'pong/pong_home.html', {'gameId': gameId})

def lobby(request, id):
	print(id)

	return render(request, 'pong/pong.html')


def pong(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('pong.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')
