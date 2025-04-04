from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Message
from django.db.models import Q

def home(request):
    """Render the home page."""
    return render(request, 'chat/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat_room')  # Redirect to chatroom after register
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})

@login_required
def new_chat(request):
    """
    Show a list of users to start a new conversation with.
    If the user selects someone they've chatted with before,
    redirects to the existing conversation.
    """
    users = User.objects.exclude(id=request.user.id)

    if request.method == 'POST':
        selected_user_id = request.POST.get('selected_user')
        if selected_user_id:
            try:
                selected_user = User.objects.get(id=selected_user_id)
                return redirect('chat_room', room_name=selected_user.username)
            except User.DoesNotExist:
                pass  # show an error message

    return render(request, 'chat/new_chat.html', {'users': users})

@login_required
def chat_room(request, room_name):
    """
    Render the chat room page.
    If room_name is provided, show the chat with that specific user.
    Otherwise, show the main chat interface with all conversations.
    """
    search_query = request.GET.get('search', '')
    users = User.objects.exclude(id=request.user.id)
    
    # Get last messages for all users for the sidebar
    user_last_messages = []
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()
        
        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })
    
    # Sort users by most recent message
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else None,
        reverse=True
    )
    
    # If we're in a specific chat room, get those messages
    chats = None
    if room_name:
        chats = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver__username=room_name)) |
            (Q(receiver=request.user) & Q(sender__username=room_name))
        )
        
        # Apply search filter if provided
        if search_query:
            chats = chats.filter(Q(content__icontains=search_query))
            
        chats = chats.order_by('timestamp')
    
    context = {
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query
    }
    
    # Add room-specific context if we're in a chat room
    if room_name:
        context.update({
            'room_name': room_name,
            'chats': chats,
        })
    
    return render(request, 'chat/chat.html', context)

@login_required
def send_message(request, receiver_username):
    """Handle sending a new message."""
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            receiver = User.objects.get(username=receiver_username)
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )
        return redirect('chat_room', room_name=receiver_username)
    return redirect('chat_room')
