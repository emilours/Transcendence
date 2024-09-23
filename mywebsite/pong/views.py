from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
# import threading
# from .scripts.multiplayer_pong import start_game


# def play(request):
# 	start_game()


def pong(request):
	# pong_thread = threading.Thread(target=start_game)
	# pong_thread.start()
	# print(f"[PONG VIEW] {threading.enumerate()}")
	# if request.user.is_authenticated:
		# redirect to login ?

	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('pong.html', request=request)

		if request.user.is_authenticated:
			username = request.user.display_name
		return JsonResponse({'html': html, 'username': username})
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
