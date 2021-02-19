from django.conf import settings
import json
import datetime
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import *
from django.contrib.auth.models import User
from account.models import *
from .chat_tools import websocket_manager
import copy
from account.auth_tools import auth_check_manager
from .system_2user_layer import layer_info_maneger

# backend for websocket


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.userID = self.scope["url_route"]["kwargs"]["room_url"].split('_')[0]
        print('\n\nconnect_info:\n'+str(self.scope)+'\n\n')
        #self.room_group_name = self.scope["url_route"]["kwargs"]["room_url"].split('_')[2]
        # user2user接收格式 'kwargs': {'room_url': '204_chatroom_4_0'}
        if self.scope["url_route"]["kwargs"]["room_url"].split('_')[3] == '0':
            self.room_group_name = self.scope["url_route"]["kwargs"]["room_url"].split('_')[2]
            self.chatroom_type = 'user2user'
        # system2user接收格式 'kwargs': {'room_url': '204_chatroom_4_1'}
        elif self.scope["url_route"]["kwargs"]["room_url"].split('_')[3] == '1':
            #self.room_group_name = self.scope["url_route"]["kwargs"]["room_url"].split('_')[2]
            self.room_group_name = 'system'+ str(self.scope["url_route"]["kwargs"]["room_url"].split('_')[2])
            self.chatroom_type = 'system2user'
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
        # 如果是系統連線,儲存user與system的layer資訊
        #if self.chatroom_type == 'system2user':
        #    layer_maneger = layer_info_maneger()
        #    layer_maneger.add_layer_info(userID=self.userID, channel_layer= self.channel_layer)

        print('websocket connect success')
    def get_channel_layer(self):
        return(self.channel_name)
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        # 刪掉儲存user與system的layer資訊
        #if self.chatroom_type == 'system2user':
        #    layer_info_maneger.del_layer_info(userID=self.userID, channel_layer= self.channel_layer)

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print('ws load jason收到的資料')
        print('\n\nreceive_data:\n'+str(text_data_json))
        
        # print(self.system_room_group_name) 
        pass_to_chat_tools = {
        'senderID' : text_data_json['senderID'],
        'chatroomID' : text_data_json['chatroomID'],
        'messageType' : text_data_json['messageType'],
        'messageText' : text_data_json['messageText'],
        'chatroom_type': self.chatroom_type}
        #now_time = datetime.datetime.now().strftime('%H:%M')
        # 儲存對話紀錄到db
        ws_manager = websocket_manager()
        msgID, time = ws_manager.chat_storge(**pass_to_chat_tools)
        now_time = str(time)
        # systemCode 暫時沒有作用,統一給0
        if text_data_json['messageType'] == 1:
            systemCode = 0
        else:
            systemCode = None

        # 在學生第一次聯絡老師此一特殊情況下，才需要同步發送訊息
        # 到第二個聊天室(也就是老師與系統的聊天室), 特殊形況的判斷寫在chat_tool
        # 若條件有滿足, 回傳聊天室的id, 若沒有滿足則回傳0
        system_chatroomID = ws_manager.query_chat_history(pass_to_chat_tools['senderID'])
        
        print('\n\nstorge message')
        # Send message to room group
        # 會發到下面的def chat_message (雖然不曉得怎麼發的)
        print('this is self.channel_layer.group_send')
        print(self.channel_layer.group_send)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, 
            {   'type' : "chat.message", # channel要求必填,不填channel會收不到
                'chatroomID':pass_to_chat_tools['chatroomID'],
                'senderID': pass_to_chat_tools['senderID'],
                'messageText': pass_to_chat_tools['messageText'],
                'messageType': pass_to_chat_tools['messageType'],
                'systemCode':systemCode,
                'messageCreateTime': now_time,
                'messageID':msgID
            },)
        print('send no.1 msg')
        # 若符合才會>1, 不符合會=0
        # 符合會在學生傳msg給老師時同步發到系統聊天室
        # system_chatroomID 格式: system_1
        if len(system_chatroomID) > 1:
            # 傳給ws的內容
            content = ws_manager.msg_maker1_system_2teacher(pass_to_chat_tools['chatroomID'])
            async_to_sync(self.channel_layer.group_send)(
                    system_chatroomID, content ,)
            print('send no.2 msg')
        else:
            pass

    # Receive message from room group
    # 收到的字典叫 "event",會回給前端
    def chat_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))
        print('send to WebSocket')
    
    # 測試是否可以直接發到特定聊天室
    # 推測這方式沒寫儲存msg應該可收到
    def system_msg_new_order_payment_remind(self):
        # 這邊先固定寫死傳看看是否成功
        self.send(text_data=json.dumps(
            {   'type' : "chat.message", # channel要求必填,不填channel會收不到
                'chatroomID':2,
                'senderID': 1,
                'messageText': 'test',
                'messageType': 3,
                'systemCode':0,
                'messageCreateTime': str(datetime.datetime.now())
            }))
        print('system send to WebSocket')

    #測試寫法2
    #c = ChatConsumer(scope = {"url_route":{"kwargs":{"room_url": '204_chatroom_4_0'}}})
    def test_send_ws_msg(self):
        async_to_sync(self.channel_layer.group_send)(
        self.room_group_name, 
        {   'type' : "chat.message", # channel要求必填,不填channel會收不到
            'chatroomID':pass_to_chat_tools['chatroomID'],
            'senderID': pass_to_chat_tools['senderID'],
            'messageText': pass_to_chat_tools['messageText'],
            'messageType': pass_to_chat_tools['messageType'],
            'systemCode':systemCode,
            'messageCreateTime': now_time
        },)
        print('system2 send to WebSocket')


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
