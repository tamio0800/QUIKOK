
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


    def test_create_a_teacher_user_function_works_properly(self):

        client = Client()
        # 先創立一門假的暫存課程
        dummy_teacher_id = 'tamio080011111'
        background_picture = open('/Users/tamiotsiu/Desktop/cuddle.png', 'rb')
        arguments_dict = {
            'dummy_teacher_id': dummy_teacher_id,
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 99,
            # 使用自訂的背景圖，code為99
            'background_picture_path': background_picture,
            # 使用自訂的背景圖，所以要給一個圖片路徑
            'lesson_title': 'test',
            'price_per_hour': 100,
            'lesson_has_one_hour_package': True,
            'trial_class_price': 99,
            'highlight_1': 'test',
            'highlight_2': 'test',
            'highlight_3': 'test',
            'lesson_intro': 'test',
            'how_does_lesson_go': 'test',
            'target_students': 'test',
            'lesson_remarks': 'test',
            'syllabus': 'test',
            'lesson_attributes': 'test'      
            }
        response = \
            self.client.post(
                path='/api/lesson/beforeSigningUpCreateOrEditLesson/',
                data=arguments_dict)
        
        print(str(response.content, 'utf8'))

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
                'data': 1
            }
        )
