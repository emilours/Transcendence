from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse 
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from frontend.models import FriendRequest

# ================================================================
# ===                       USER LOGS                          ===
# ================================================================

User = get_user_model()

@require_POST
def signin(request):
    if request.method == 'POST':
        print('**************************************')
        print('SIGNIN')
        print('**************************************')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # test
        print('***********************************')
        print(email)
        print(password)
        print('***********************************')
        
        if not email or not password:
            messages.error(request, "Email and password are required.")
            return HttpResponse("Email and password are required.", status=401)
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return HttpResponse("You have successfully logged in.", status=201)
        else:
            messages.error(request, "Invalid email or password.")
            return HttpResponse("Invalid email or password.", status=401)
    else:
        messages.error(request, "Log in process failed.")
        return HttpResponse("Log in process failed.", status=401)

@require_POST
def signup(request):
    if request.method == 'POST':
        print('*************************************')
        print('SIGNUP')
        print('*************************************')
        firstname = request.POST.get('first name')
        lastname = request.POST.get('last name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        display_name = request.POST.get('display_name')
        avatar = request.FILES.get('avatar') 

        # test
        print('***********************************')
        print(firstname)
        print(lastname)
        print(email)
        print(password1)
        print(password2)
        print(display_name)
        print(avatar)
        print('***********************************')
        
        if not firstname or not lastname or not email or not password1 or not password2 or not display_name:
            messages.error(request, "Fields are required.")
            return HttpResponse("Fields are required.", status=400)
        
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return HttpResponse("Passwords do not match.", status=400)

        User = get_user_model()

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return HttpResponse("Email is already in use.", status=400)
        
        if User.objects.filter(display_name=display_name).exists():
            messages.error(request, "Username is already taken.")
            return HttpResponse("Username is already taken.", status=400)

        user = User.objects.create_user(email=email, password=password1)
        user.first_name = firstname
        user.last_name = lastname
        user.display_name = display_name
        if avatar:
            user.avatar = avatar
        user.save()

        user = authenticate(request, username=email, password=password1)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Account successfully created and logged in.")
            return HttpResponse("Account successfully created and logged in.", status=201)
        else:
            messages.error(request, "Authentication failed.")
            return HttpResponse("Authentication failed.", status=401)
    else:
        messages.error(request, "Sign up process failed.")
        return HttpResponse("Sign up process failed.", status=400)

# @login_required
@require_POST
def signout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
        return HttpResponse("You have successfully logged out.", status=200)
    else:
        messages.warning(request, "You are not currently logged in.")
        return HttpResponse("You are not currently logged in.", status=403)

def is_online(user):
    if user.last_login:
        return timezone.now() - user.last_login < timedelta(minutes=5)
    return False

def contact(request):
    def is_online(user):
        if user.last_login:
            return timezone.now() - user.last_login < timedelta(minutes=5)
        return False

    users = User.objects.all()
    online_users = []
    offline_users = []

    for user in users:
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'display_name': getattr(user, 'display_name', ''),
            'avatar': str(user.avatar.url) if user.avatar else '',
            'last_login': user.last_login,
        }

        # Compter les demandes reçues par l'utilisateur
        received_requests_count = FriendRequest.objects.filter(
            receiver=user,
            is_active=True
        ).count()
        user_data['received_requests_count'] = received_requests_count

        # Compter les demandes envoyées par l'utilisateur
        sent_requests_count = FriendRequest.objects.filter(
            sender=user,
            is_active=True
        ).count()
        user_data['sent_requests_count'] = sent_requests_count

        # Vérifiez si l'utilisateur a une demande en attente envoyée à l'utilisateur actuel
        has_pending_request = FriendRequest.objects.filter(
            sender=user,
            receiver=request.user,
            is_active=True
        ).exists()
        user_data['has_pending_request'] = has_pending_request

        if is_online(user):
            online_users.append(user_data)
        else:
            offline_users.append(user_data)

    return JsonResponse({
        'online': online_users,
        'offline': offline_users
    })

# ================================================================
# ===              USER FRIEND REQUESTS                        ===
# ================================================================

@login_required
@require_POST
def send_friend_request(request):
    receiver_email = request.POST.get('receiver_email')
    
    if not receiver_email:
        # return HttpResponse("Invalid email address provided.", status=400)
        return JsonResponse({"error": "Invalid email address provided."}, status=400)
    
    try:
        receiver = User.objects.get(email=receiver_email)
        if receiver == request.user:
            # return HttpResonse("You cannot send a friend request to yourself.", status=400)
            return JsonResponse({"error": "You cannot send a friend request to yourself."}, status=400)
        
        print('***********************************')
        print(f"Sender: {request.user.email}")
        print(f"Receiver: {receiver.email}")
        print('***********************************')

        FriendRequest.objects.create(sender=request.user, receiver=receiver)
        messages.success(request, "Friend request sent.")
        # return HttpResponse("Friend request sent", status=200)
        return JsonResponse({"message": "Friend request sent."}, status=200)
        
    except User.DoesNotExist:
        messages.error(request, "User with this email does not exist.")
        # return HttpResponse("User with this email does not exist.", status=404)
        return JsonResponse({"error": "User with this email does not exist."}, status=404)
    except Exception as e:
        # return HttpResponse(f"An error occurred: {str(e)}", status=500)
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@login_required
@require_POST
def accept_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, receiver=request.user)
        friend_request.accept()
        messages.success(request, "Friend request accepted.")
        return JsonResponse({"message": "Friend request accepted."}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    
@login_required
@require_POST
def refuse_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, receiver=request.user)
        friend_request.refuse()
        messages.success(request, "Friend request refused.")
        return JsonResponse({"message": "Friend request refused."}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@login_required
@require_POST
def cancel_friend_request(request, friend_request_id):
    try:
        friend_request = FriendRequest.objects.get(id=friend_request_id, sender=request.user)
        friend_request.cancel()
        messages.success(request, "Friend request cancelled.")
        return JsonResponse({"message": "Friend request cancelled."}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Friend request not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@login_required
def view_received_requests(request):
    received_requests = FriendRequest.objects.filter(receiver=request.user, is_accepted=False)
    requests_list = [{"id": fr.id, "sender": str(fr.sender), "timestamp": fr.timestamp} for fr in received_requests]
    return JsonResponse({"requests": requests_list})


@login_required
def debug_friend_requests(request):
    try:
        emi = User.objects.get(email='emilie@gmail.com')
        zak = User.objects.get(email='zak@gmail.com')

        # Créez une demande d'ami
        fr = FriendRequest.objects.create(sender=emi, receiver=zak, is_active=True)
        response_text = f"Created FriendRequest: {fr}\n"

        # Vérifiez les demandes envoyées et reçues
        sent_requests = FriendRequest.objects.filter(sender=emi)
        received_requests = FriendRequest.objects.filter(receiver=zak)

        # Impressions pour déboguer
        response_text += f"Sent requests by emi: {list(sent_requests)}\n"
        response_text += f"Received requests by zak: {list(received_requests)}\n"

        return HttpResponse(response_text, content_type="text/plain")

    except User.DoesNotExist as e:
        return HttpResponse(f"Error: User not found: {str(e)}", status=404, content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"Error: An error occurred: {str(e)}", status=500, content_type="text/plain")