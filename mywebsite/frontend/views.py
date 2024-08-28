from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
# from .forms import LoginForm, SignUpForm

def home(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('home.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')

# def login(request):
# 	if request.method == 'POST':
# 		form = LoginForm(request, data=request.POST)
# 		if form.is_valid():
# 			# Authentication logic here
# 			return redirect('home')
# 	else:
# 		form = LoginForm()

# 	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
# 		html = render_to_string('login.html', {'form': form}, request=request)
# 		return JsonResponse({'html': html})
# 	return render(request, 'base.html', {'form': form})

# def signup(request):
# 	if request.method == 'POST':
# 		form = SignUpForm(request.POST)
# 		if form.is_valid():
# 			form.save()
# 			return redirect('login')
# 	else:
# 		form = SignUpForm()

# 	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
# 		html = render_to_string('signup.html', {'form': form}, request=request)
# 		return JsonResponse({'html': html})
# 	return render(request, 'base.html', {'form': form})

def leaderboard(request):
	return render(request, 'leaderboard.html')

def games(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		html = render_to_string('games.html', request=request)
		return JsonResponse({'html': html})
	return render(request, 'base.html')
