from django.test import TestCase
from chatroom.models import Messages, chat_room,chatroom_info_user2user
from chatroom.consumers import ChatConsumer
from django.contrib.auth.models import User
from channels.testing import WebsocketCommunicator
from django.urls import path
import pytest
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer
import datetime
from unittest import skip
#python3 manage.py test chatroom/ --settings=Quikok.settings_for_test
@skip
class test_consumer(TestCase):
    def setUp(self):
        chatroom_info_user2user.objects.create(
            teacher_auth_id=1,
            student_auth_id=7,
            parent_auth_id= -1,
            chatroom_type='teacher2student',
            created_time= datetime.datetime.now()
        ).save()
        
        print('建立user2user 聊天室')
    @pytest.mark.asyncio
    async def test_my_consumer(self):
        channel_layer = get_channel_layer()

        application = URLRouter([
            path('ws/chat/<str:room_url>/', ChatConsumer),])

        communicator = WebsocketCommunicator(application, "/ws/chat/7_chatroom_1_0/")
        connected, subprotocol = await communicator.connect()
        assert connected
        # generate valid channel name
        channel_name = await channel_layer.new_channel()
        print('channel name in test')
        print(channel_name)
        await communicator.send_json_to({
        #'channel': channel_name,
        'data': 'some-data', 
        'senderID': 1,
        'chatroomID' : 1,
        'messageType' : 1,
        'messageText' : 'test'})

        from_channel_layer = await channel_layer.receive(channel_name)
        assert from_channel_layer == {'data': 'some-data'}
        
        # Test on connection welcome message
        #message = await communicator.receive_from()
        #assert message == 'test'
        # Close
        await communicator.disconnect()

    def tearDown(self):
        chatroom_info_user2user.objects.all().delete()


##class test_chatroom_consumer(TestCase):
#    def test__system_msg(self):
#        self.client = Client()
#        response = self.client.post(path='ws/chat/7_chatroom_1_0/')
#        self.assertEqual(response.status_code, 200)