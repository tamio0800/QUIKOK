from django.http import response
from django.test import RequestFactory, TestCase,Client
from django.contrib.auth.models import Permission, User, Group
from django.urls.conf import path
from account.models import (student_profile, teacher_profile, user_token, feedback,
                                general_available_time,specific_available_time)
from account.auth_tools import auth_check_manager
from datetime import datetime, timedelta, date as date_function
from lesson.models import lesson_card
import os, shutil
from unittest import skip
from account.email_sending import email_manager
from django.core import mail

# python manage.py test account/ --settings=Quikok.settings_for_test
class Auth_Related_Functions_Test(TestCase):

    def test_auth_check_exist(self):
        # 測試這個函式是否存在，並且應該回傳status='success', errCode=None, errMsg=None
        # self.factory = RequestFactory()
        self.client = Client()
        response = self.client.get(path='/authCheck/')
        self.assertEqual(response.status_code, 200)

class Teacher_Profile_Test(TestCase):

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
        client = Client()
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
        client.post(path='/api/account/signupTeacher/', data=data)
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            True
        )
        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')

    
    def test_send_welcom_email_when_create_teacher(self):
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
        test_username = 'test201218_teacher_user@test.com'
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
        response = client.post(path='/api/account/signupTeacher/', data=data)
        # 建立會員有成功
        self.assertIn('success', str(response.content))
        # 確認有寄出通知信
        self.assertEqual(mail.outbox[0].subject, 'Quikok!開課 註冊成功通知')

    def test_teacher_available_and_specific_time_created_after_signing_up(self):
        
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
        '''
        禮拜一: 時段 1, 2, 3, 4, 5;
        禮拜二: 時段 11, 13, 15, 17, 19, 21, 22, 25, 33;
        禮拜五: 時段 1, 9, 27, 28, 41;
        '''

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

        # 先確定真的建立了大概半年左右的 specific_times
        # 因為最高只建立了未來183天的資料，所以不會大於 t + 183 天
        self.assertGreater(
            date_function.today() + timedelta(days=185),
            specific_available_time.objects.latest('date').date,
            specific_available_time.objects.values()
        )
        # 因為建立了未來183天的資料，所以不會小於 t + 150 天
        self.assertLess(
            date_function.today() + timedelta(days=150),
            specific_available_time.objects.latest('date').date,
            specific_available_time.objects.values()
        )

        # 因為登錄了禮拜一、二、五的資料，應該要有這幾個紀錄，並且沒有其他weekdays的紀錄
        self.assertListEqual(
            list(set([_.weekday() for _ in specific_available_time.objects.values_list('date', flat=True)])),
            [0, 1, 4],
            list(set([_.weekday() for _ in specific_available_time.objects.values_list('date', flat=True)]))
        )

        # 選 倒數第7筆記錄 & 第15筆記錄 查驗 時段的正確性
        self.assertListEqual(
            [
                list(specific_available_time.objects.all())[-7].time,
                list(specific_available_time.objects.all())[15].time,
            ],
            [
                general_available_time.objects.filter(week= \
                    list(specific_available_time.objects.all())[-7].date.weekday()).first().time,
                general_available_time.objects.filter(week= \
                    list(specific_available_time.objects.all())[15].date.weekday()).first().time,
            ]
        )
        # print(specific_available_time.objects.values())


    def test_teacher_available_and_specific_time_synchronized_after_editting_profile(self):
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:11,13,15,17,19,21,22,25,33;4:1,9,27,28,41;'
        }
        '''
        禮拜一: 時段 1, 2, 3, 4, 5;
        禮拜二: 時段 11, 13, 15, 17, 19, 21, 22, 25, 33;
        禮拜五: 時段 1, 9, 27, 28, 41;
        '''
        print(f'teacher_post_data:  {teacher_post_data}')
        client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        
        teacher_post_data['intro'] = '因為最近事情比較多，暫時沒有可以預約的時間唷~~'
        teacher_post_data['userID'] = 1
        teacher_post_data['nickname'] = '一個新的測試暱稱'
        teacher_post_data['teacher_general_availabale_time'] = ''

        # 更新老師的資料
        response = client.post(path='/api/account/editTeacherProfile/', data=teacher_post_data)
        self.assertIn(
            'success',
            str(response.content, 'utf8')
        )

        # 確認資料真的更新了
        self.assertEqual(
            (
                teacher_post_data['intro'],
                teacher_post_data['nickname'],
                0
            ),
            (
                teacher_profile.objects.filter(auth_id=1).first().intro,
                teacher_profile.objects.filter(auth_id=1).first().nickname,
                general_available_time.objects.filter(teacher_model__auth_id=1).count()
            ),
            general_available_time.objects.filter(teacher_model__auth_id=1).values()
        )
        
        # 此時應該什麼都沒有才對
        self.assertEqual(
            ( 
                0,
                0
            ),
            (
                general_available_time.objects.filter(teacher_model__auth_id=1).count(),
                specific_available_time.objects.filter(teacher_model__auth_id=1).count()
            ),
            (general_available_time.objects.values(), specific_available_time.objects.values())
        )

        teacher_post_data['teacher_general_availabale_time'] = \
            '2:30,31,32,33,34,35;3:4,5,6,15;4:22,21,28,29;5:17,19,31,32,33;6:40,41,42,43;'
        # 改為 禮拜二、三、四、五、六、日
        response = client.post(path='/api/account/editTeacherProfile/', data=teacher_post_data)
        # 刪除資料夾
        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')

        self.assertIn(
            'success', str(response.content, 'utf8')
        )

        self.assertEqual(
            5,
            general_available_time.objects.filter(teacher_model__auth_id=1).count(),
            general_available_time.objects.values()
        )
        # 因為最高只建立了未來183天的資料，所以不會大於 t + 183 天
        self.assertGreater(
            date_function.today() + timedelta(days=185),
            specific_available_time.objects.latest('date').date,
            specific_available_time.objects.values()
        )
        # 因為建立了未來183天的資料，所以不會小於 t + 150 天
        self.assertLess(
            date_function.today() + timedelta(days=150),
            specific_available_time.objects.latest('date').date,
            specific_available_time.objects.values()
        )

        self.assertListEqual(
            list(set([_.weekday() for _ in specific_available_time.objects.values_list('date', flat=True)])),
            [2, 3, 4, 5, 6],
            list(set([_.weekday() for _ in specific_available_time.objects.values_list('date', flat=True)]))
        )

        # 選 倒數第7筆記錄 & 第15筆記錄 查驗 時段的正確性
        self.assertListEqual(
            [
                list(specific_available_time.objects.all())[-7].time,
                list(specific_available_time.objects.all())[15].time,
            ],
            [
                general_available_time.objects.filter(week= \
                    list(specific_available_time.objects.all())[-7].date.weekday()).first().time,
                general_available_time.objects.filter(week= \
                    list(specific_available_time.objects.all())[15].date.weekday()).first().time,
            ]
        )


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
        
        #print(f'before general_available_time:  \
        #    {general_available_time.objects.values().filter(teacher_model__auth_id=teacher_post_data["userID"])}')

        response = client.post(path='/api/account/editTeacherProfile/', data=teacher_post_data)

        #print(f'after general_available_time:  \
        #    {general_available_time.objects.values().filter(teacher_model__auth_id=teacher_post_data["userID"])}')
        
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
        
        #print(
        #    f'os.path.getsize(teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:]): \
        #    {os.path.getsize(teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:])}'
        #    )

        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')


    def test_edit_teacher_available_times_works(self):
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
        self.assertEqual(os.path.isdir('user_upload/teachers/' + test_username), False)

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
        self.assertEqual(general_available_time.objects.filter(
            teacher_model=teacher_profile.objects.first()
        ).count(), 2)  # 應該只有兩筆資料
        before_specific_times_count = \
            specific_available_time.objects.filter(
                teacher_model=teacher_profile.objects.first()
            ).count()

        teacher_post_data['userID'] = 1
        teacher_post_data['teacher_general_availabale_time'] = \
            '6:2,3,4,5,6,6,27;0:28,29,30,31;1:17,18,19,20,21;2:14,15,16,39,40,41,42,43,44;3:24,25,26,27;4:29,30,31,32;5:43,44,45,46;'
        
        response = client.post(path='/api/account/editTeacherProfile/', data=teacher_post_data)
        self.assertEqual(general_available_time.objects.filter(
            teacher_model=teacher_profile.objects.first()
        ).count(), 7)  # 應該有7筆資料


class Student_Test(TestCase):

    def setUp(self):
        self.test_username = 'test_student_username@test.com'
        self.client = Client()
        Group.objects.bulk_create([
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ])


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_username)
        except:
            pass


    def test_if_student_created_properly(self):
        
        student_post_data = {
            'regEmail': self.test_username,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        resoponse = self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        self.assertIn(
            'success',
            str(resoponse.content, 'utf8')
        )
        self.assertEqual(
            student_post_data['regName'],
            student_profile.objects.filter(auth_id=1).first().nickname,
            student_profile.objects.values()
        )
        self.assertTrue(
            os.path.isdir(f'user_upload/students/{self.test_username}')
        )
    
    def test_send_welcom_email_when_create_teacher(self):
        client = Client()
        test_username = 'test_student@test.com'
        data = {
            'regEmail': test_username,
            'regPwd': '00000000',
            'regName': 'test_name',
            'regNickname': 'test_nickname',
            'regBirth': '2000-01-01',
            'regGender': '0',
            'regRole': 'test',
            'regMobile': '0912-345678',
            'regNotifiemail': ''
       }
        response = client.post(path='/api/account/signupStudent/', data=data)
        # 建立會員有成功
        self.assertIn('success', str(response.content))
        # 確認有寄出通知信
        self.assertEqual(mail.outbox[0].subject, 'Quikok!開課 註冊成功通知')

    def test_if_student_editted_properly(self):

        student_post_data = {
            'regEmail': self.test_username,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        student_post_data['userID'] = 1
        student_post_data['mobile'] = '0911-234567'
        student_post_data['nickname'] = '新的學生測試暱稱'
        student_post_data['intro'] = '新的學生測試自我介紹啦啦啦'
        student_post_data['upload_snapshot'] = \
            open('user_upload/temp/before_signed_up/tamio0800111111/customized_lesson_background.jpg', 'rb')
        student_post_data['update_someone_by_email'] = 'updated1@test.com;updated2@test.com;'

        response = self.client.post(path='/api/account/editStudentProfile/', data=student_post_data)

        self.assertIn(
            'success',
            str(response.content, 'utf8'),
            response
        )

        self.assertEqual(
            (
                student_post_data['mobile'],
                student_post_data['nickname'],
                student_post_data['update_someone_by_email'],
                f'/user_upload/students/{self.test_username}/thumbnail.jpg',
                student_post_data['intro']
            ),
            (
                student_profile.objects.first().mobile,
                student_profile.objects.first().nickname,
                student_profile.objects.first().update_someone_by_email,
                student_profile.objects.first().thumbnail_dir,
                student_profile.objects.first().intro
            )
        )

        self.assertTrue(
            os.path.isfile(student_profile.objects.first().thumbnail_dir[1:])
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



class BANKING_INFO_TEST(TestCase):
    '''
    用來測試帳戶回傳資訊是否正確
    '''
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
        teacher_post_data['regEmail'] = self.test_teacher_name2,
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)

        self.test_teacher_name3 = 'test_teacher3_user@test.com'
        teacher_post_data['regEmail'] = self.test_teacher_name3,
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建了3個老師
        
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
        # 建了3個學生


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name1)
            shutil.rmtree('user_upload/students/' + self.test_student_name2)
            shutil.rmtree('user_upload/students/' + self.test_student_name3)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name1)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name2)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name2)
        except:
            pass


    def test_get_banking_infomation_work(self):
        # 先測試老師的資料是否回傳正確
        query_post_data = {
            'userID': teacher_profile.objects.get(id=2).auth_id,
            'type': 'teacher'
        }
        response = \
            self.client.post(path='/api/account/getBankingInfomation/', data=query_post_data)
        self.assertEqual(200, response.status_code)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"bank_name": ""', str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"balance": 0'),
            str(response.content, "utf8"))

        teacher_2 = teacher_profile.objects.get(id=2)
        teacher_2.withholding_balance = 300
        teacher_2.bank_code = '555'
        teacher_2.save()
        response = \
            self.client.post(path='/api/account/getBankingInfomation/', data=query_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"balance": 0'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"bank_code": "555"'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"withholding_balance": 300'),
            str(response.content, "utf8"))

        query_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'type': 'teacher'
        }
        response = \
            self.client.post(path='/api/account/getBankingInfomation/', data=query_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertIn('"errCode": "1"', str(response.content, "utf8"))

        query_post_data['type'] = 'student'
        response = \
            self.client.post(path='/api/account/getBankingInfomation/', data=query_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"bank_account_code": ""', str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"withholding_balance": 0'),
            str(response.content, "utf8"))

        student_2 = student_profile.objects.get(id=2)
        student_2.balance = 200
        student_2.withholding_balance = 1300
        student_2.bank_code = '55'
        student_2.bank_account_code = '077'
        student_2.bank_name = 'XXXXswss'
        student_2.save()
        response = \
            self.client.post(path='/api/account/getBankingInfomation/', data=query_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"balance": 200'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"bank_code": "55"'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"withholding_balance": 1300'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"bank_code": "55"'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"bank_account_code": "077"'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"bank_name": "XXXXswss"'),
            str(response.content, "utf8"))


