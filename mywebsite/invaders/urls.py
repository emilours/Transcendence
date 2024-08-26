from django.urls import path
from . import views

urlpatterns = [
	path('invaders/', views.invaders, name='invaders'),
]
