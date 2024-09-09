from django.urls import path
from .views import invaders, save_score

urlpatterns = [
	path('', invaders, name='invaders'),
	path('save_score/', save_score, name='save_score'),
]
