from django.urls import path
from . import views
from .views import save_match
from .views import invader_leaderboard

urlpatterns = [
	path("", views.invaders, name='invaders'),
	path('save_match/', save_match, name='save_match'),
	path('invader_leaderboard/', invader_leaderboard, name='invader_leaderboard'),
]
