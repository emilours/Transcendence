from django.urls import path
from . import views

urlpatterns = [
	path('', views.pong),
	path('lobby<int:id>/', views.lobby)
]
