from django.urls import path
from . import views as auth_views
from . import api_views
from .views import signout

urlpatterns = [
    path('signup/', auth_views.signup, name='signup'),
    path('signin/', auth_views.signin, name='signin'),
    path('signout/', signout, name='signout'),
    path('send_friend_request/', auth_views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:friend_request_id>/', auth_views.accept_friend_request, name='accept_friend_request'),
    path('refuse_friend_request/<int:friend_request_id>/', auth_views.refuse_friend_request, name='refuse_friend_request'),
    path('cancel_friend_request/<int:friend_request_id>/', auth_views.cancel_friend_request, name='cancel_friend_request'),
    path('remove_friend/<int:friend_id>/', auth_views.remove_friend, name='remove_friend'),
    path('update_profile/', auth_views.update_profile, name='update_profile'),
    path('delete_profile/', auth_views.delete_profile, name='delete_profile'),
    path('update_password/', auth_views.update_password, name='update_password'),
    path('request_anonymization/', auth_views.request_anonymization, name='request_anonymization'),

    # API URLs last
    path('oauth/complete/42/', api_views.callback_42, name='callback_42'),
]
