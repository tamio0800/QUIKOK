
from django.test import RequestFactory, TestCase
from django.test import Client
from django.contrib.auth.models import Permission, User, Group
from account.models import student_profile, teacher_profile, user_token
from account.auth_check import auth_check_manager
from datetime import datetime, timedelta

# python manage.py test lesson/ --settings=Quikok.settings_for_test
class Auth_Related_Functions_Test(TestCase):


    def test_auth_check_exist(self):
        # 測試這個函式是否存在，並且應該回傳status='success', errCode=None, errMsg=None
        # self.factory = RequestFactory()
        self.client = Client()
        response = self.client.get(path='/authCheck/')
        self.assertEqual(response.status_code, 200)


    def test_create_a_teacher_after_setting_up_a_class_exist(self):
        # 測試 sign_up_after_setup_a_clcreate_a_teacher_after_setting_up_a_classass 這個函式存在
        client = Client()
        response = client.post(path='/api/account/create_a_teacher_after_setting_up_a_class/')
        self.assertEqual(response.status_code, 200)


    def test_create_a_teacher_after_setting_up_a_class_receive_dummy_teacher_id_variable(self):
        # 測試 sign_up_after_setup_a_clcreate_a_teacher_after_setting_up_a_classass 這個函式存在
        client = Client()

        dummy_teacher_id = ''
        response = client.post(path='/api/account/create_a_teacher_after_setting_up_a_class/')
        self.assertEqual(response.status_code, 200)

