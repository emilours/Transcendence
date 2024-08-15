# from django.urls import path
# from . import views

# urlpatterns = [
# 	path('', views.home, name='home'),
# 	path('signup/', views.signup, name='signup'),
# 	path('login/', views.login, name='login'),
# ]


from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='home'),
	path('login/', views.index, name='login'),
	path('signup/', views.index, name='signup'),
	path('home/content/', views.home_content, name='home_content'),
	path('login/content/', views.login_content, name='login_content'),
	path('signup/content/', views.signup_content, name='signup_content'),
	path('leaderboard/', views.leaderboard, name='leaderboard'),
]

