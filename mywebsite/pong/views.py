from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
import threading
from .scripts.multiplayer_pong import start_game


# def play(request):
# 	start_game()


def pong(request):
	pong_thread = threading.Thread(target=start_game)
	pong_thread.start()
	print(f"[PONG VIEW] {threading.enumerate()}")
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('pong.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')
