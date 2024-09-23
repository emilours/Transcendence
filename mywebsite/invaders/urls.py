from django.urls import path
from . import views
from .views import save_match

urlpatterns = [
	path("", views.invaders, name='invaders'),
	path('save_match/', save_match, name='save_match'),
]
