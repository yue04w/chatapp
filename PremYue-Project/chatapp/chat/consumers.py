import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']
        
        sender = await self.get_user(sender_username)
        if sender:
            receiver_username = self.room_name.replace(sender_username, '').replace('_', '')
            receiver = await self.get_user(receiver_username)
            if receiver:
                await self.save_message(sender, receiver, message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
    
    @staticmethod
    async def get_user(username):
        try:
            return await User.objects.aget(username=username)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    async def save_message(sender, receiver, message):
        await Message.objects.acreate(sender=sender, receiver=receiver, content=message)
