from django.urls import path
from . import views as auth_views

urlpatterns = [
    path('signup/', auth_views.signup, name='signup'),
    path('signin/', auth_views.signin, name='signin'),
    path('signout/', auth_views.signout, name='signout'),
    path('contactList/', auth_views.contact, name='contactList'),  # URL pour mes tests
    path('send_friend_request/', auth_views.contact, name='send_friend_request'),
    path('debug_friend_requests/', auth_views.contact, name='debug_friend_requests'),
]