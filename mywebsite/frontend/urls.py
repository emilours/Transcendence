from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='index'),
	path('home/', views.home, name='home'),
	path('login/', views.login, name='login'),
	path('signup/', views.signup, name='signup'),
	path('profile/', views.profile, name='profile'),
	path('edit_profile/', views.edit_profile, name='edit_profile'),
	path('edit_password/', views.edit_password, name='edit_password'),
	path('games/', views.games, name='games'),
	path('leaderboard/', views.leaderboard, name='leaderboard'),
	path('dashboard/<str:username>/', views.user_dashboard, name='user_dashboard'),
	path('load_header/', views.load_header, name='load_header'),
	path('contact/', views.contact, name='contact'),
	path('deleted_profile/', views.deleted_profile, name='deleted_profile'),
	path('error_api/', views.error_api, name='error_api'),
]
