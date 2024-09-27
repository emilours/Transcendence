from django.urls import path
from . import views

urlpatterns = [
	path('', views.pong),
    path('SaveLocalPongMatch/', views.SaveLocalPongMatch),
]
