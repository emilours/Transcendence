from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string

def invaders(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('invaders.html', request=request)
		return JsonResponse({'html': html})

# def invaders(request):
# 	return render(request, 'invaders.html')
