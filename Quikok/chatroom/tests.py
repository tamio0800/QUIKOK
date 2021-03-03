from django.test import TestCase,Client
from chatroom.models import (chatroom_info_user2user, chatroom_info_Mr_Q2user, 
                chat_history_user2user, chat_history_Mr_Q2user)
from chatroom.consumers import ChatConsumer
from django.contrib.auth.models import User, Group
from channels.testing import WebsocketCommunicator
from django.urls import path
import pytest
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer
import datetime
from unittest import skip
#python3 manage.py test chatroom/ --settings=Quikok.settings_for_test

class test_chat_tools(TestCase):
    def setUp(self):
        self.client = Client()        
        Group.objects.bulk_create(
            [
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ]
        )
        # 建了3個老師，注意！第一個auth=1會被用來當"system"聊天室！
        self.test_teacher_name1 = 'test_teacher1_user@test.com'
        teacher_post_data = {
            'regEmail': self.test_teacher_name1,
            'regPwd': '00000000',
            'regName': 'test_name',
            'regNickname': 'test_nickname',
            'regBirth': '2000-01-01',
            'regGender': '0',
            'intro': 'test_intro',
            'regMobile': '0912-345678',
            'tutor_experience': '一年以下',
            'subject_type': 'test_subject',
            'education_1': 'education_1_test',
            'education_2': 'education_2_test',
            'education_3': 'education_3_test',
            'company': 'test_company',
            'special_exp': 'test_special_exp',
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:1,2,3,4,5;4:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        
        self.test_teacher_name2 = 'test_teacher2_user@test.com'
        teacher_post_data['regEmail'] = self.test_teacher_name2
        teacher_post_data['regPwd'] = '11111111'
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)

        self.test_teacher_name3 = 'test_teacher3_user@test.com'
        teacher_post_data['regEmail'] = self.test_teacher_name3
        teacher_post_data['regPwd'] = '22222222'
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        
        # 建了3個學生
        self.test_student_name1 = 'test_student1@a.com'
        student_post_data = {
            'regEmail': self.test_student_name1,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name2 = 'test_student2@a.com'
        student_post_data['regEmail'] = self.test_student_name2
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name3 = 'test_student3@a.com'
        student_post_data['regEmail'] = self.test_student_name3
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        
        # 建立聊天室
        chatroom_info_user2user.objects.create(
            teacher_auth_id = 1,
            student_auth_id = 7,
            parent_auth_id = -1,
            chatroom_type='teacher2student',
            created_time= datetime.datetime.now()
        ).save()
        
        print('建立user2user 聊天室')

    def test_check_when_create_teacher_create_a_system2user_chatroom(self):
        '''確認創建使用者時，都有順利建立使用者與系統(system的聊天室），
            注意，1號自己是老師又是系統，在測試時不用特別管這件事'''
        #確認目前所有人數是否與Mr_Q的聊天室長度一致
        self.assertEqual(User.objects.all().count(),
            chatroom_info_Mr_Q2user.objects.all().count())



@skip
class test_websocket_consumer(TestCase):
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