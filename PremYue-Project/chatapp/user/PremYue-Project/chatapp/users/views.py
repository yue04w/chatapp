from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_page(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='bp')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('chat_room', room_name='bp')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'login.html')

@login_required
def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('chat_room', room_name='bp') 

    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1') 
        confirm_password = request.POST.get('password2')  

        # Check if passwords match
        if password1 != confirm_password:
            messages.error(request, 'Passwords do not match. Please try again.')
            return render(request, 'register.html')

        # Check if email is already taken
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use. Please try another one.')
            return render(request, 'register.html')

        # Create the new user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, 'Signup successful! You can now log in.')
        return redirect('login')

    return render(request, 'register.html')
