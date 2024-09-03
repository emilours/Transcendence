from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from django.utils import timezone
from frontend.models import FriendRequest, FriendList, CustomUser
import os

User = get_user_model()

# # ================================================================================================================================================================
# # ===                                                      USER LOGS                                                                                           ===
# # ================================================================================================================================================================

@require_POST
def signin(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email or not password:
        return JsonResponse({"error": "Email and password are required."}, status=400)

    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        user.is_active = True
        user.save()
        return JsonResponse({"message": "You have successfully logged in."}, status=200)
    else:
        return JsonResponse({"error": "Invalid email or password."}, status=401)

@require_POST
def signup(request):
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    email = request.POST.get('email')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    display_name = request.POST.get('display_name')
    avatar = request.FILES.get('avatar')

    if not firstname or not lastname or not email or not password1 or not password2 or not display_name:
        return JsonResponse({"error": "All fields are required."}, status=400)

    if password1 != password2:
        return JsonResponse({"error": "Passwords do not match."}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email is already in use."}, status=400)

    if User.objects.filter(display_name=display_name).exists():
        return JsonResponse({"error": "Username is already taken."}, status=400)

    if avatar:
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(avatar.name)[1].lower()
        if ext not in valid_extensions:
            return JsonResponse({"error": f"Unsupported file extension: {ext}. Allowed extensions are: .jpg, .jpeg, .png, .gif."}, status=400)

    max_avatar_size = 2 * 1024 * 1024
    if avatar and avatar.size > max_avatar_size:
        return JsonResponse({"error": f"File size exceeds the maximum limit of 2MB."}, status=400)

    user = User.objects.create_user(email=email, password=password1)
    user.first_name = firstname
    user.last_name = lastname
    user.display_name = display_name
    if avatar:
        user.avatar = avatar
    user.save()

    user.sent_requests_count = 0
    user.received_requests_count = 0
    user.accepted_requests_count = 0
    user.declined_requests_count = 0

    user = authenticate(request, email=email, password=password1)
    if user is not None:
        login(request, user)
        return JsonResponse({"message": "Account successfully created and logged in."}, status=201)
    else:
        return JsonResponse({"error": "Authentication failed."}, status=401)

@login_required
@require_POST
def signout(request):
    if request.user.is_authenticated:
        request.user.is_active = False
        request.user.save()
        logout(request)
        return JsonResponse({"message": "You have successfully logged out."}, status=200)
    else:
        return JsonResponse({"error": "You are not currently logged in."}, status=403)

def is_online(user):
    return user.last_login and timezone.now() - user.last_login < timedelta(minutes=45)

@login_required
def contact(request):
    users = CustomUser.objects.all()
    online_users = []
    offline_users = []

    for user in users:
        friend_list = getattr(user, 'friend_list', None)
        friends_count = friend_list.friend_count() if friend_list else 0

        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'display_name': user.display_name,
            'avatar': str(user.avatar.url) if user.avatar else '',
            'last_login': user.last_login,
            'received_requests_count': user.received_requests_count,
            'sent_requests_count': user.sent_requests_count,
            'friends_count': friends_count,
            'declined_requests_count': user.declined_requests_count,
        }

        if is_online(user):
            online_users.append(user_data)
        else:
            offline_users.append(user_data)

    return JsonResponse({'online': online_users, 'offline': offline_users})

# # ================================================================================================================================================================
# # ===                                                      FRIEND REQUESTS                                                                                     ===
# # ================================================================================================================================================================

@login_required
@require_POST
def send_friend_request(request):
    receiver_email = request.POST.get('receiver_email')

    if not receiver_email:
        return JsonResponse({"error": "Invalid email address provided."}, status=400)

    try:
        receiver = User.objects.get(email=receiver_email)

        if receiver == request.user:
            return JsonResponse({"error": "You cannot send a friend request to yourself."}, status=400)

        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            return JsonResponse({"error": "Friend request already sent."}, status=400)
        # revoir si le receiver a déjà envoyé une demande d'amitié

        FriendRequest.objects.create(sender=request.user, receiver=receiver)

        return JsonResponse({"message": "Friend request sent."}, status=200)

    except User.DoesNotExist:
        return JsonResponse({"error": "User with this email does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@login_required
@require_POST
def accept_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, receiver=request.user)
        friend_request.accept()
        return JsonResponse({"message": "Friend request accepted."}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@login_required
@require_POST
def refuse_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, receiver=request.user)
        friend_request.decline()
        return JsonResponse({"message": "Friend request refused."}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@login_required
@require_POST
def cancel_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, sender=request.user)
        friend_request.cancel()
        return JsonResponse({"message": "Friend request cancelled."}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

