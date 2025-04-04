from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_room, name='chat_room'),  # Now /chat/ works directly

    path('', views.home, name='home'),
    path('chat/', views.chat_room, name='chat_room'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room_with_user'),
    path('register/', views.register, name='register'),
    #This is for individual chat room
    path('send/<str:receiver_username>/', views.send_message, name='send_message'),
    path('new/', views.new_chat, name='new_chat'),
]
