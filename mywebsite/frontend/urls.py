from django.urls import path
from . import views

urlpatterns = [
	path('home/', views.home, name='home'),
	# path('login/', views.login, name='login'),
	# path('signup/', views.signup, name='signup'),
	path('games/', views.games, name='games'),
	# path('leaderboard/', views.leaderboard, name='leaderboard'),
]
