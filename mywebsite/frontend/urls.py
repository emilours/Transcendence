from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='index'),
	path('home/', views.home, name='home'),
	path('login/', views.login, name='login'),
	path('signup/', views.signup, name='signup'),
	path('profile/', views.profile, name='profile'),
	path('edit_profile/', views.edit_profile, name='edit_profile'),
	path('games/', views.games, name='games'),
	path('leaderboard/', views.leaderboard, name='leaderboard'),
	path('load_header/', views.load_header, name='load_header'),
]
