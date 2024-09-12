from django.urls import path
from . import views
from .views import save_arcade_score

urlpatterns = [
	path("", views.invaders, name='invaders'),
	path('save_arcade_score/', save_arcade_score, name='save_arcade_score'),
]

