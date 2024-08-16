from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('home', views.index, name='home'),
	path('signup', views.signup_view, name='signup'),
	path('login', views.login_view, name='login'),
]