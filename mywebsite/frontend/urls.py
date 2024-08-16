from django.urls import path
from . import views

urlpatterns = [
	path('home/', views.home, name='home'),
	path('login/', views.login, name='login'),
	path('signup/', views.signup, name='signup'),
	# path('leaderboard/', views.leaderboard, name='leaderboard'),
]

# from django.urls import path
# from ajax.views import home, compute

# urlpatterns = [
# 	path('', home, name="home"),
# 	path('compute/', compute, name="compute"),
# ]
