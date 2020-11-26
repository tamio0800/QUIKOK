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
        # 接收格式 'kwargs': {'room_url': '204_chatroom_4_0'}
        if self.scope["url_route"]["kwargs"]["room_url"].split('_')[3] == 0:
            self.room_group_name = self.scope["url_route"]["kwargs"]["room_url"].split('_')[2]
        # 接收格式 'kwargs': {'room_url': '204_chatroom_4_1'}
        elif self.scope["url_route"]["kwargs"]["room_url"].split('_')[3] == 1:
            self.room_group_name = 'system'+ str(self.scope["url_route"]["kwargs"]["room_url"].split('_')[2])
            print(type(self.room_group_name))
        else: #以後聊天室如果有更多種類可以加這
            pass
        print('channel name:')
        print(self.channel_name)
        print('room_group_name')
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

        # 查詢老師跟學生是否為第一次聊天
        #chatroom = chatroom_info_user2user.objects.filter(Q(student_auth_id=pass_data_to_chat_tools['userID'])|Q(teacher_auth_id=teacher_authID))


        #now_time = datetime.datetime.now().strftime('%H:%M')
        ws_manager = websocket_manager()
        msgID, time, is_first_msg = ws_manager.chat_storge(**self.pass_data_to_chat_tools)
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
        print('this is self.channel_layer.group_send')
        print(self.channel_layer.group_send)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, # channel_name
            {   'type' : "chat.message", # channel要求必填,不填channel會收不到
                'chatroomID':self.pass_data_to_chat_tools['chatID'],
                'senderID': self.pass_data_to_chat_tools['userID'],
                'messageText': self.pass_data_to_chat_tools['message'],
                'messageType': self.pass_data_to_chat_tools['messageType'],
                'systemCode':systemCode,
                'messageCreateTime': str(now_time)
            })
        #async_to_sync('21')(
        #    self.room_group_name, # channel_name
        #    {   'type' : "chat.message", # channel要求必填,不填channel會收不到
        #        'chatroomID':21,
        #        'senderID': 204,
        #        'messageText': 'test',
        #        'messageType': self.pass_data_to_chat_tools['messageType'],
        #        'systemCode':systemCode,
        #        'messageCreateTime': str(now_time)
        #    })

        print('send_somthing to somewhere')

    # Receive message from room group
    # 收到的字典叫 "event",會回給前端
    def chat_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))
        print('send to WebSocket')
    
    # 測試是否可以同時發兩個聊天室
#    def chat_send_system_msg(self,event):
#        self.send(text_data=json.dumps(event))
#        print('system send to WebSocket')


#class ChatSystem(ChatConsumer):
#    self.room_group_name =self.scope["url_route"]["kwargs"]["room_url"].split('_')[2]

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
