from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse 
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

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

def signout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out.")
        return HttpResponse("You have successfully logged out.", status=200)
    else:
        messages.warning(request, "You are not currently logged in.")
        return HttpResponse("You are not currently logged in.", status=403)

def contact(request):
    users = User.objects.all().values('id', 'email', 'first_name', 'last_name', 'password', 'display_name', 'avatar')
    user_list = list(users)
    return JsonResponse(user_list, safe=False)