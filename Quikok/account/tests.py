
from django.test import RequestFactory, TestCase
from django.test import Client
from django.contrib.auth.models import Permission, User, Group
from account.models import student_profile, teacher_profile, user_token, feedback, general_available_time
from account.auth_tools import auth_check_manager
from datetime import datetime, timedelta
from lesson.models import lesson_card
import os, shutil
from unittest import skip

#python manage.py test account/ --settings=Quikok.settings_for_test
class Auth_Related_Functions_Test(TestCase):

    def test_auth_check_exist(self):
        # 測試這個函式是否存在，並且應該回傳status='success', errCode=None, errMsg=None
        # self.factory = RequestFactory()
        self.client = Client()
        response = self.client.get(path='/authCheck/')
        self.assertEqual(response.status_code, 200)

class Teacher_Test(TestCase):

    def test_create_teacher_receive_can_mkdir(self):
        Group.objects.bulk_create(
            [
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ]
        )
        self.client = Client()
        test_username = 'test201218_teacher_user@test.com'
        try:
            shutil.rmtree('user_upload/teachers/' + test_username)
        except:
            pass
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            False
        )
        data = {
            'regEmail': test_username,
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=data)
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            True
        )
        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')

    
    def test_get_teacher_available_time(self):
        Group.objects.bulk_create(
            [
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ]
        )
        client = Client()
        test_username = 'test_teacher_user@test.com'
        teacher_available_time = '0:1,2,3,4,5;1:11,13,15,17,19,21,22,25,33;4:1,9,27,28,41;'
        try:
            shutil.rmtree('user_upload/teachers/' + test_username)
        except:
            pass
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            False
        )
        data = {
            'regEmail': test_username,
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
            'teacher_general_availabale_time': teacher_available_time
        }
        client.post(path='/api/account/signupTeacher/', data=data)
        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')
       
        the_general_available_time = general_available_time.objects.filter(teacher_model_id=1)

        self.assertEqual(
            the_general_available_time.filter(week=0).first().time,
            '1,2,3,4,5'
        )
        self.assertEqual(
            the_general_available_time.filter(week=1).first().time,
            '11,13,15,17,19,21,22,25,33'
        )
        self.assertEqual(
            the_general_available_time.filter(week=4).first().time,
            '1,9,27,28,41'
        )

    #def test_get_teacher_available_time(self):
    #    self.test_get_teacher_available_time()
    #    client = Client()
    #    teacher_auth_id = 1
    #    response = client.post(path='api/account/getTeacherAvailableTime/', teacher_auth_id)
    #    # 理論上要回傳




    @skip
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

    @skip
    def test_lesson_card_is_created_after_teacher_signed_up_with_dummy_teacher_id(self):
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
        
        print(lesson_card.objects.values().first())
        self.assertEqual(
            lesson_card.objects.all().count(),
            1
        )

        self.assertEqual(
            lesson_card.objects.all().first().lesson_title,
            'test'
        )


class Feedback_Test(TestCase):
    
    def test_feedback_exist(self):
        # 測試這個函式是否存在
        self.client = Client()
        response = self.client.post(path='/api/account/feedback/')
        self.assertEqual(response.status_code, 200)


    def test_feedback_received_data_from_frontend(self):
        # 測試傳送「問題反應」的資訊給後端，後端是否有收到
        self.client = Client()

        who_are_you = 'test_user'
        contact = 'test_user@test.com'
        problem = 'here is a test problem to test if views function could received.'
        on_which_page = '/test/url/'
        is_signed_in = True
        post_data = {
            'who_are_you': who_are_you,
            'contact': contact,
            'problem': problem,
            'on_which_page': on_which_page,
            'is_signed_in': is_signed_in
        }
        response = self.client.post(path='/api/account/feedback/', data=post_data)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': '謝謝您告訴我們這件事，我們會火速處理、並協助您解決這個問題，請再留意您的Email或手機唷。'
            }
        )


    def test_feedback_written_data_into_DB(self):
        # 測試傳送「問題反應」的資訊給後端，後端是否有收到
        self.client = Client()
        who_are_you = 'test_user'
        contact = 'test_user@test.com'
        problem = 'here is a test problem to test if views function could received.'
        on_which_page = '/test/url/'
        is_signed_in = True
        post_data = {
            'who_are_you': who_are_you,
            'contact': contact,
            'problem': problem,
            'on_which_page': on_which_page,
            'is_signed_in': is_signed_in
        }
        self.client.post(path='/api/account/feedback/', data=post_data)
        self.assertEqual(feedback.objects.all().count(), 1, feedback.objects.values())
        self.assertEqual(feedback.objects.first().who_are_you, who_are_you)
        self.assertEqual(feedback.objects.first().contact, contact)
        self.assertEqual(feedback.objects.first().problem, problem)
        self.assertEqual(feedback.objects.first().on_which_page, on_which_page)
        self.assertEqual(feedback.objects.first().is_signed_in, is_signed_in)


class EMAIL_SENDING_TEST(TestCase):

    def test_email_could_send(self):
        self.client = Client()
        response = self.client.get('/api/account/send_email/')
        self.assertIn('Success', str(response.content, 'utf8'),
        str(response.content, 'utf8'))


class PROFILE_EDITTING_TEST(TestCase):

    def test_edit_teacher_profile_works_properly(self):
        client = Client()
        # 要先建立老師才能做測試
        Group.objects.bulk_create(
            [
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ]
        )

        test_username = 'test201224_teacher_user@test.com'
        try:
            shutil.rmtree('user_upload/teachers/' + test_username)
        except:
            pass
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            False
        )

        teacher_post_data = {
            'regEmail': test_username,
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;5:6,7,8,9,10;'
        }
        response = client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 先註冊老師
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1
            }
        )
        self.assertEqual(
            teacher_profile.objects.filter(auth_id=1).first().auth_id,
            1
        )

        teacher_post_data['userID'] = 1
        teacher_post_data['nickname'] = '新的暱稱'
        teacher_post_data['intro'] = '新的自我介紹歐耶'
        teacher_post_data['mobile'] = '0911-222345'
        teacher_post_data['teacher_general_availabale_time'] = '0:1,2,3,4,5;5:6,7,8,9,10;3:10,11,12;'
        teacher_post_data['upload_snapshot'] = ''
        
        print(f'before general_available_time:  \
            {general_available_time.objects.values().filter(teacher_model__auth_id=teacher_post_data["userID"])}')

        response = client.post(path='/api/account/editTeacherProfile/', data=teacher_post_data)

        print(f'after general_available_time:  \
            {general_available_time.objects.values().filter(teacher_model__auth_id=teacher_post_data["userID"])}')
        
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
            }
        )  # views function有成功拿到資料

        # 測試有沒有照實寫入
        self.assertEqual(
            (
                teacher_profile.objects.filter(username=test_username).first().nickname,
                teacher_profile.objects.filter(username=test_username).first().intro,
                teacher_profile.objects.filter(username=test_username).first().mobile,
                general_available_time.objects.filter(
                    teacher_model__auth_id=teacher_post_data['userID']).filter(week=3).first().time
            ),
            (
                teacher_post_data['nickname'],
                teacher_post_data['intro'],
                teacher_post_data['mobile'],
                '10,11,12'
            ),
            teacher_profile.objects.values()
        )

        # 測試圖片也可以編輯
        row_thumbnail_pic_path = 'user_upload/temp/before_signed_up/tamio0800111111/customized_lesson_background.jpg'
        picture_in_binary = open(row_thumbnail_pic_path, 'rb')
        teacher_post_data['upload_snapshot'] = picture_in_binary

        self.assertNotIn(
            'thumbnail',
            teacher_profile.objects.filter(username=test_username).first().thumbnail_dir,
        )  # 在還沒有更新前，應該沒有大頭貼

        response = client.post(path='/api/account/editTeacherProfile/', data=teacher_post_data)

        self.assertEqual(
            os.path.getsize(row_thumbnail_pic_path),
            os.path.getsize(teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:]),
            teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:]
        )  # 更新後，兩個大頭貼應該一樣了
        
        print(
            f'os.path.getsize(teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:]): \
            {os.path.getsize(teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:])}'
            )

        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')

        # 接下來測試看看課程小卡有沒有連動更改
        

