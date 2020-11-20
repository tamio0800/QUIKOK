from django.conf import settings
import json
import datetime
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import *
from django.contrib.auth.models import User
from account.models import *
from .chat_tools import websocket_manager

# backend for websocket


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print('成功!')
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
        response = dict()
        pass_data_to_chat_tools = dict()
        
        text_data_json = json.loads(text_data)
        print('ws load jason收到的資料')
        print('\n\nreceive_data:\n'+str(text_data_json))
        
        pass_data_to_chat_tools = {
        'userID' : text_data_json['userID'],
        'chatID' : text_data_json['chatID'],
        'messageType' : text_data_json['messageType'],
        'message' : text_data_json['messageText']}

        now_time = datetime.datetime.now().strftime('%H:%M')

        #if False in pass_data_to_chat_tools.values(): 
        #    response['status'] = 'failed'
        #    response['errCode'] = '0'
        #    response['errMsg'] = 'Received Arguments Failed.'
        #    response['data'] = None
        #    return JsonResponse(response)

        #else:
        ws_manager = websocket_manager()
        #response['status'], response['errCode'], response['errMsg'], response['data'] =\
        ws_manager.chat_storge(**pass_data_to_chat_tools)
        #return JsonResponse(response)


        #user_id =self.scope["url_route"]["kwargs"]["room_url"].split('_')[0]
        #group_id = self.room_group_name
        ### 新增結構
        #pass_data_to_chat_tools = dict()
        #key_from_frontend = ['userID', 'chatID','messageType','messageText']

        #ws_manager = websocket_manager()
        #ws_manager.chat_storge(chatID = group_id,sender=userID,message=messageText,
        #messageType = messageType )
        ###
        #group=chat_room.objects.get(id=group_id)
        #group.date=datetime.datetime.now()
        #group.save()
        print('\n\nstorge message')
        #user = 
        user=User.objects.get(id=pass_data_to_chat_tools['userID'])
        #Messages.objects.create(sender=user, message=pass_data_to_chat_tools['message'], 
        #                        group=pass_data_to_chat_tools['chatID'])

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': pass_data_to_chat_tools['message'],
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
