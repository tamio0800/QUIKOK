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
        self.pass_data_to_chat_tools = dict()
        
        text_data_json = json.loads(text_data)
        print('ws load jason收到的資料')
        print('\n\nreceive_data:\n'+str(text_data_json))
        
        self.pass_data_to_chat_tools = {
        'userID' : text_data_json['userID'],
        'chatID' : text_data_json['chatID'],
        'messageType' : text_data_json['messageType'],
        'message' : text_data_json['messageText']}

        #now_time = datetime.datetime.now().strftime('%H:%M')
        ws_manager = websocket_manager()
        msgID, time = ws_manager.chat_storge(**self.pass_data_to_chat_tools)
        now_time = str(time)
        # systemCode 暫時沒有作用,統一給0
        if text_data_json['messageType'] == 1:
            systemCode = 0
        else:
            systemCode = None
        print('\n\nstorge message')
        #user=User.objects.get(id=self.pass_data_to_chat_tools['userID'])
        # Send message to room group
        # 會發到下面的chat_message (雖然不曉得怎麼發的)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, # channel_name
            {   'type' : "chat.message", # channel要求必填
                'chatID':self.pass_data_to_chat_tools['chatID'],
                'userID': self.pass_data_to_chat_tools['userID'],
                'messageText': self.pass_data_to_chat_tools['message'],
                'messageType': self.pass_data_to_chat_tools['messageType'],
                'systemCode':systemCode,
                'messageCreateTime': str(now_time)
            })
        print('send_somthing to somewhere')

    # Receive message from room group
    # 收到的字典叫 "event"
    # 這個會回給前端
    def chat_message(self, event):
        return_to_ws =dict()
        #for k,v in event.values()
        print('收到event')
        #event['messageCreateTime'] = str(now_time)
        #message = event['message']
        #now_time = event['now_time']
        #user = event['user']
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))
        print('send to WebSocket')

        #if False in pass_data_to_chat_tools.values(): 
        #    response['status'] = 'failed'
        #    response['errCode'] = '0'
        #    response['errMsg'] = 'Received Arguments Failed.'
        #    response['data'] = None
        #    return JsonResponse(response)

        #else:
        #response['status'], response['errCode'], response['errMsg'], response['data'] =\
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
