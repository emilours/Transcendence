from django.urls import path
from . import views

# urlpatterns = [
# 	path('', views.home, name='home'),
# 	path('signup/', views.signup, name='signup'),
# 	path('login/', views.login, name='login'),
# 	# path('logout/', views.logout, name='logout'),
# ]


urlpatterns = [
	path('', views.index, name='index'),
	path('home', views.index, name='home'),
	path('signup', views.signup_view, name='signup'),
	path('login', views.login_view, name='login'),
]

