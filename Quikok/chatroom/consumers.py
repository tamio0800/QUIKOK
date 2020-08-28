from django.conf import settings
import json
import datetime
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Messages, chat_room
from django.contrib.auth.models import User

# backend for websocket


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        
        print('\n\nconnect_info:\n'+str(self.scope)+'\n\n')
        self.room_group_name =self.scope["url_route"]["kwargs"]["room_url"].split('_')[2]
        
        
        print(self.room_group_name)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        self.accept()
        print('websocket connect success')

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print('\n\nreceive_data:\n'+str(text_data_json))
        message = text_data_json['message']
        
        now_time = datetime.datetime.now().strftime('%H:%M')
        
        if not message:
            return
        user_id =self.scope["url_route"]["kwargs"]["room_url"].split('_')[0]
        group_id = self.room_group_name
        group=chat_room.objects.get(id=group_id)
        group.date=datetime.datetime.now()
        group.save()
        print('\n\nstorge message')
        user=User.objects.get(id=user_id)
        Messages.objects.create(sender=user, message=message, group=group)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username,
                'now_time': now_time
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        now_time = event['now_time']
        user = event['user']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'now_time': now_time,
        }))

'''

asynchronous version
'''

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
#
#
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event['message']
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
#
