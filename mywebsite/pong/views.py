from django.shortcuts import render

# Create your views here.
def pong(request):
	liveGames = 0
	gameId = liveGames
	liveGames += 1
	return render(request, 'pong/home.html', {'gameId': gameId})

def lobby(request, id):
	print(id)

	return render(request, 'pong/pong.html')
