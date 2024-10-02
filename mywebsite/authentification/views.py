from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from frontend.models import FriendRequest, FriendList, CustomUser, validate_no_special_characters
from django.db import IntegrityError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout, get_user_model
from django.utils.timezone import localtime
from django.db import transaction
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404, render
from django.http import StreamingHttpResponse
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.conf import settings
import asyncio
import json
import os
import time

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

    if not User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Please sign up first."}, status=404)

    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        user.is_online = True
        user.save(update_fields=['is_online'])
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

    try:
        validate_no_special_characters(firstname)
        validate_no_special_characters(lastname)
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if password1 != password2:
        return JsonResponse({"error": "Passwords do not match."}, status=400)

    try:
        validate_password(password1)
    except ValidationError as e:
        return JsonResponse({"error": " ".join(e.messages)}, status=400)

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
        request.user.is_online = False
        request.user.save(update_fields=['is_online'])
        logout(request)
        return JsonResponse({"message": "You have successfully logged out."}, status=200)
    else:
        return JsonResponse({"error": "You are not currently logged in."}, status=403)

def is_online(user):
    return user.last_login and timezone.now() - user.last_login < timedelta(minutes=45)

def contact(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "No users authenticated"}, status=401)
    users = CustomUser.objects.all()
    online_users = []
    offline_users = []

    for user in users:
        friend_list = getattr(user, 'friend_list', None)
        friends_count = friend_list.friend_count() if friend_list else 0

        last_login_local = localtime(user.last_login) if user.last_login else None
        formatted_last_login = last_login_local.strftime('%Y-%m-%d %H:%M') if last_login_local else ''

        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'display_name': user.display_name,
            'avatar': str(user.avatar.url) if user.avatar else '',
            'last_login': formatted_last_login,
            'is_online' : user.is_online,
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
@transaction.atomic
def send_friend_request(request):
    try:
        receiver_display_name = request.POST.get('receiver_display_name')

        if not receiver_display_name:
            return JsonResponse({"error": "A username is required."}, status=400)

        receiver = CustomUser.objects.filter(display_name=receiver_display_name).first()

        if not receiver:
            return JsonResponse({"error": "User not found."}, status=404)

        if receiver == request.user:
            return JsonResponse({"error": "Cannot send friend request to yourself."}, status=400)

        if FriendRequest.objects.filter(sender=receiver, receiver=request.user, status='pending').exists():
            return JsonResponse({"error": "Friend request already received."}, status=400)

        sender = request.user

        FriendRequest.objects.filter(sender=sender, receiver=receiver, status='declined').delete()

        friend_request, created = FriendRequest.objects.get_or_create(
            sender=sender,
            receiver=receiver,
            defaults={'status': 'pending'}
        )

        if created:
            return JsonResponse({"message": "Friend request sent successfully."}, status=200)
        else:
            return JsonResponse({"error": "Friend request already exists."}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_POST
@transaction.atomic
def accept_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, receiver=request.user)
        friend_request.accept()
        return JsonResponse({"message": "Friend request accepted.", "status": "accepted"}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_POST
@transaction.atomic
def refuse_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, receiver=request.user)
        friend_request.decline()
        return JsonResponse({"message": "Friend request refused.", "status": "declined"}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_POST
@transaction.atomic
def cancel_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, sender=request.user)
        friend_request.cancel()
        return JsonResponse({"message": "Friend request cancelled.", "status": "declined"}, status=200)
    except FriendRequest.DoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@require_POST
@transaction.atomic
def remove_friend(request, friend_id):
    try:
        friend_list = FriendList.objects.get(user=request.user)
        friend = CustomUser.objects.get(id=friend_id)
        friend_list.unfriend(friend)
        return JsonResponse({"message": "Friend removed successfully."}, status=200)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "Friend not found."}, status=404)
    except FriendList.DoesNotExist:
        return JsonResponse({"error": "Friend list not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

# # ================================================================================================================================================================
# # ===                                                      USER UPDATE FORM                                                                                    ===
# # ================================================================================================================================================================

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user

        email = request.POST.get('email', user.email).strip()
        first_name = request.POST.get('first_name', user.first_name).strip()
        last_name = request.POST.get('last_name', user.last_name).strip()
        display_name = request.POST.get('display_name', user.display_name).strip()
        avatar = request.FILES.get('avatar', None)
        avatar_choice = request.POST.get('avatar_choice', None)

        try:
            validate_no_special_characters(first_name)
            validate_no_special_characters(last_name)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

        if user.is_api_authenticated and email != user.email:
            return JsonResponse({
                'error': 'For security reasons, please update your email directly through the 42 intranet platform.'
            }, status=403)

        if email == '':
            email = user.email

        if email != user.email:
            if CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
                return JsonResponse({
                    'error': 'This email address is already in use.',
                    'email': email
                }, status=400)

        if display_name == '':
            display_name = user.display_name

        if display_name != user.display_name:
            if CustomUser.objects.filter(display_name=display_name).exclude(pk=user.pk).exists():
                return JsonResponse({
                    'error': 'This display name is already in use.',
                    'display_name': display_name
                }, status=400)

        if first_name == '':
            first_name = user.first_name

        if first_name != user.first_name:
            if CustomUser.objects.filter(first_name=first_name).exclude(pk=user.pk).exists():
                return JsonResponse({
                    'error': 'This display name is already in use.',
                    'first_name': first_name
                }, status=400)

        if last_name == '':
            last_name = user.last_name

        if last_name != user.last_name:
            if CustomUser.objects.filter(last_name=last_name).exclude(pk=user.pk).exists():
                return JsonResponse({
                    'error': 'This display name is already in use.',
                    'last_name': last_name
                }, status=400)

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.display_name = display_name

        if avatar:
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in valid_extensions:
                return JsonResponse({"error": f"Unsupported file extension: {ext}. Allowed extensions are: .jpg, .jpeg, .png, .gif."}, status=400)

        max_avatar_size = 2 * 1024 * 1024
        if avatar and avatar.size > max_avatar_size:
            return JsonResponse({"error": f"File size exceeds the maximum limit of 2MB."}, status=400)

        if avatar:
            user.avatar = avatar
        elif avatar_choice:
            user.avatar = avatar_choice

        try:
            user.save()
            return JsonResponse({
                'message': 'Profile successfully updated',
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'display_name': user.display_name,
                    'avatar': user.avatar.url if user.avatar else None,
                }
            }, status=200)
        except IntegrityError as e:
            return JsonResponse({
                'error': 'An error occurred while updating the profile.',
                'details': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': 'An unexpected error occurred.',
                'details': str(e)
            }, status=400)

    return JsonResponse({
        'error': 'Invalid request method.'
    }, status=405)

# # ================================================================================================================================================================
# # ===                                                      DELETE USER ACCOUNT                                                                                ===
# # ================================================================================================================================================================

@login_required
@require_POST
def delete_profile(request):
    if request.method == 'POST':
        user = request.user

        try:
            Token.objects.filter(user=user).delete()
            user.delete()
            return JsonResponse({
                'message': 'Profile and all associated data successfully deleted.'
            }, status=200)
        except IntegrityError as e:
            return JsonResponse({
                'error': 'An error occurred while deleting the profile.',
                'details': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': 'An unexpected error occurred.',
                'details': str(e)
            }, status=400)

    return JsonResponse({
        'error': 'Invalid request method.'
    }, status=405)

# # ================================================================================================================================================================
# # ===                                                      USER UPDATE PASSWORD                                                                                ===
# # ================================================================================================================================================================

@login_required
def update_password(request):
    if request.method == 'POST':
        user = request.user

        if user.is_api_authenticated:
            return JsonResponse({
                'error': 'For security reasons, please update your password directly through the 42 intranet platform.'
            }, status=403)

        form = PasswordChangeForm(user, request.POST)

        if form.is_valid():
            new_password = form.cleaned_data.get('new_password1')

            if check_password(new_password, user.password):
                return JsonResponse({
                    'error': 'New password cannot be the same as the current password.'
                }, status=400)

            user = form.save()
            update_session_auth_hash(request, user)
            return JsonResponse({
                'message': 'Password successfully updated'
            }, status=200)
        else:
            errors = {field: [error['message'] for error in form.errors.get_json_data()[field]] for field in form.errors}
            return JsonResponse({
                'error': 'Please correct the errors below.',
                'errors': errors
            }, status=400)

    return JsonResponse({
        'error': 'Invalid request method.'
    }, status=405)

# # ================================================================================================================================================================
# # ===                                                      ANONYMIZATION                                                                                       ===
# # ================================================================================================================================================================

@login_required
def request_anonymization(request):
    user = request.user

    try:
        with transaction.atomic():
            unique_suffix = get_random_string(length=8)

            avatar_dir = os.path.join(settings.MEDIA_ROOT, 'img/avatars/')

            deleted_files = []
            for filename in os.listdir(avatar_dir):
                if user.display_name in filename:
                    file_path = os.path.join(avatar_dir, filename)

                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_files.append(file_path)

            user.avatar = 'img/avatars/avatar0.jpg'
            user.display_name = f'Anonymous_{unique_suffix}'
            user.first_name = 'Anonymous'
            user.last_name = 'Anonymous'
            user.save()

            return JsonResponse({'message': 'Your data has been anonymized successfully.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# # ================================================================================================================================================================
# # ===                                                      SSE                                                                                                 ===
# # ================================================================================================================================================================

@login_required
def sse(request):
    async def event_stream():
        last_status = []
        last_number = await asyncio.to_thread(check_friendlist_update, request.user)
        try:
            while True:
                status_update = await asyncio.to_thread(check_friend_request_update, request.user)
                number_update = await asyncio.to_thread(check_friendlist_update, request.user)

                if status_update != last_status or last_number != number_update:
                    combined_update = {
                        "friend_requests": status_update,
                        "friend_count": number_update
                    }
                    yield f"data: {json.dumps(combined_update)}\n\n"

                    last_status = status_update
                    last_number = number_update

                await asyncio.sleep(5)
        except asyncio.CancelledError:
            print('Stream closed')
            return
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def check_friend_request_update(user):
    pending_requests = FriendRequest.objects.filter(
        Q(sender=user) | Q(receiver=user),
        status__in=['accepted', 'declined', 'pending']
    )

    if pending_requests.exists():
        return [
            {
                "id": friend_request.id,
                "sender": friend_request.sender.display_name,
                "receiver": friend_request.receiver.display_name,
                "status": friend_request.status
            }
            for friend_request in pending_requests
        ]
    return []

def check_friendlist_update(user):
    try:
        friendlist = FriendList.objects.get(user=user)
        return friendlist.friend_count()
    except FriendList.DoesNotExist:
        return 0

# def sse_test(request):
#     def event_stream():
#         for i in range(5):
#             time.sleep(1)
#             yield f"data: Hello SSE {i}\n\n"
#     return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
