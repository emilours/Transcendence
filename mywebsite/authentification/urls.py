from django.urls import path
from . import views as auth_views

urlpatterns = [
    path('signup/', auth_views.signup, name='signup'),
    path('signin/', auth_views.signin, name='signin'),
    path('contactList/', auth_views.contact, name='contactList'),  # URL test
]
