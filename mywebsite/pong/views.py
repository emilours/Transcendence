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


# def pong(request):
# 	# pong_thread = threading.Thread(target=start_game)
# 	# pong_thread.start()
# 	# print(f"[PONG VIEW] {threading.enumerate()}")
# 	# if request.user.is_authenticated:
# 		# redirect to login ?

# 	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
# 		html = render_to_string('pong.html', request=request)

# 		if request.user.is_authenticated:
# 			user_data = {
# 				'id': request.user.id,
# 				'username': request.user.username,
# 				'email': request.user.email,
# 				'is_authenticated': True
# 			}
# 		else:
# 			user_data = {
# 				'is_authenticated': False
# 			}
# 		return JsonResponse({'html': html, 'user': user_data})
# 	return render(request, 'base.html')
