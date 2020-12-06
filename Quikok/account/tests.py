
from django.test import RequestFactory, TestCase
from django.test import Client
from django.contrib.auth.models import Permission, User, Group
from account.models import student_profile, teacher_profile, user_token
from account.auth_check import auth_check_manager
from datetime import datetime, timedelta
from account.models import teacher_profile

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


    def test_create_a_teacher_after_setting_up_a_class_required_dummy_teacher_id_variable(self):
        # 測試 sign_up_after_setup_a_clcreate_a_teacher_after_setting_up_a_classass 這個函式存在
        client = Client()
        post_data = {
            'dummy_teacher_id': 'tamio080011111'
        }
        response = client.post(
            path='/api/account/create_a_teacher_after_setting_up_a_class/',
            data=post_data)
        print(str(response.content, encoding='utf8'))
        
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': None
            }
        )

    def test_create_a_teacher_user_function_works_properly(self):
        client = Client()
        post_data = {
            # 這邊創立要建立老師的註冊資料
            'dummy_teacher_id': 'tamio080011111',
            'regEmail': 'test_teacher_user@test.com',
            'regPwd': '00000000',
            'regName': 'test_name',
            'regNickname': 'test_nickname',
            'regBirth': '2000-01-01',
            'regGender': '0',
            'intro': 'test_intro',
            'regMobile': '0912-345-678',
            'tutor_experience': '一年以下',
            'subject_type': 'test_subject',
            'education_1': 'education_1_test',
            'education_2': 'education_2_test',
            'education_3': 'education_3_test',
            'company': 'test_company',
            'special_exp': 'test_special_exp',
            'teacher_general_availabale_time': '0:1,2,3,4,5'
        }

        response = client.post(
            path='/api/account/signupTeacher/',
            data=post_data
        )
        print(str(response.content, encoding='utf8'))
        print(teacher_profile.objects.values()
        )
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': None
            }
        )
