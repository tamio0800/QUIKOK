from django.test import TestCase,Client
from django.contrib.auth.models import Group
from django.urls.conf import path
from account.models import (student_profile, teacher_profile, feedback,
                            general_available_time,specific_available_time)
from account.models import invitation_code_detail, user_invitation_code_mapping
from datetime import datetime, timedelta, date as date_function
import os, shutil
from unittest import skip
from django.core import mail
from time import time, sleep
from django.db.models import Q
from django.conf import settings
import asyncio
import threading
from threading import Thread
from django.core.files.uploadedfile import SimpleUploadedFile
# 設定環境變數 DEV_MODE 為true >>  export DEV_MODE=true
# 取消環境變數 DEV_MODE >> unset DEV_MODE
# python3 manage.py test account/ --settings=Quikok.settings_for_test
class Auth_Related_Functions_Test(TestCase):
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
        teacher_post_data['regEmail'] = self.test_teacher_name2
        teacher_post_data['regPwd'] = '11111111'
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)

        self.test_teacher_name3 = 'test_teacher3_user@test.com'
        teacher_post_data['regEmail'] = self.test_teacher_name3
        teacher_post_data['regPwd'] = '22222222'
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


    def test_auth_check_exist(self):
        # 測試這個函式是否存在，並且應該回傳status='success', errCode=None, errMsg=None
        # self.factory = RequestFactory()
        self.client = Client()
        response = self.client.get(path='/authCheck/')
        self.assertEqual(response.status_code, 200)


    def test_change_password_exist(self):
        '''
        測試更改密碼的api存在
        '''
        self.client = Client()
        response = self.client.post(path='/api/account/memberChangePassword/')
        self.assertEqual(response.status_code, 200)


    def test_change_password_received_and_validated_arguments(self):
        '''
        測試修改密碼的這支api能不能正確收取到參數。
        '''
        chg_pwd_post_data = {
            'userID': 3,
            'oldUserPwd': 'dwedewikrj23oi5joiu4trjoufj432jt34i82043jiefwo',
            'newUserPwd': 'djwiofdjewu89320894u2304jr23j980rhudnsaljrjfeas'}
        response = \
            self.client.post(path='/api/account/memberChangePassword/', data=chg_pwd_post_data)
        # 因為是隨便輸入的，密碼不符合 （錯誤2或錯誤3）
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertTrue('"errCode": "2"' in str(response.content, "utf8") or
            '"errCode": "3"' in str(response.content, "utf8"))

        #chg_pwd_post_data['newUserPwd'] = 'djwiofdjewu89320894u2304jr23j980rhudnsaljrjfeas'
        #response = \
        #    self.client.post(path='/api/account/memberChangePassword/', data=chg_pwd_post_data)
        #self.assertIn('failed', str(response.content, "utf8"))
        #self.assertIn('"errCode": "2"', str(response.content, "utf8"))
        # 因為密碼不對

    
    def test_change_password_work_on_teachers(self):
        '''
        測試老師更改密碼可以成功
        '''
        teacher_1 = teacher_profile.objects.get(id=1)
        # self.fail(teacher_1.password)
        # 00000000
        chg_pwd_post_data = {
            'userID': teacher_1.auth_id,
            'oldUserPwd': teacher_1.password,
            'newUserPwd': '44444444'}
        response = \
            self.client.post(path='/api/account/memberChangePassword/', data=chg_pwd_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertEqual('44444444', teacher_profile.objects.get(id=1).password)


    def test_change_password_work_on_students(self):
        '''
        測試學生更改密碼可以成功
        '''
        student_1 = student_profile.objects.get(id=1)
        # self.fail(teacher_1.password)
        chg_pwd_post_data = {
            'userID': student_1.auth_id,
            'oldUserPwd': student_1.password,
            'newUserPwd': '99999999'}
        response = \
            self.client.post(path='/api/account/memberChangePassword/', data=chg_pwd_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertEqual('99999999', student_profile.objects.get(id=1).password)


class Teacher_Profile_Test_setup(TestCase):
    ''' 這個測試是新版的老師測試，舊的版本沒有先setup資料做測試，
        為了增加測試效益而新增這個class
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:1,2,3,4,5;4:1,2,3,4,5;',
            'youtube_video_url' : 'https://www.youtube.com/watch?v=OSxfx9p5bfI'
        }
        teacher_post_data['upload_picture_1'] = SimpleUploadedFile(name='test_1.jpg', 
                    content=open('test_folder/test_file/test_1.jpg', 'rb').read(), content_type='image/jpg')
        teacher_post_data['upload_picture_2'] = SimpleUploadedFile(name='test_2.jpg', 
                    content=open('test_folder/test_file/test_2.jpg', 'rb').read(), content_type='image/jpg')
        teacher_post_data['upload_picture_3'] = SimpleUploadedFile(name='test_3.jpg', 
                    content=open('test_folder/test_file/test_2.jpg', 'rb').read(), content_type='image/jpg')
        # 上傳三張圖片
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)

        # 確認有建立
        self.assertEqual(teacher_profile.objects.all().count(),1)
        self.assertEqual(teacher_profile.objects.get(id=1).upload_picture_4_location, '')



    def test_teacher_sighup_upload_info_pic(self):
        '''測次當老師註冊時, 上傳5張額度的圖片(非大頭照)的情況
            1. 檔案是否正確地被傳到老師資料夾中
            2. teacher profile 的路徑是否正確
        '''
        
        teacher_post_data = {
            'regEmail': 'test_teacher2@test.com',
            'regPwd': '00000000',
            'regName': 'teacher2',
            'regNickname': 'nick_teacher2',
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:1,2,3,4,5;4:1,2,3,4,5;',
            
        }

        teacher_post_data['upload_picture_1'] = SimpleUploadedFile(name='test_1.jpg', 
                    content=open('test_folder/test_file/test_1.jpg', 'rb').read(), content_type='image/jpg')
        teacher_post_data['upload_picture_2'] = SimpleUploadedFile(name='test_2.jpg', 
                    content=open('test_folder/test_file/test_2.jpg', 'rb').read(), content_type='image/jpg')
        teacher_post_data['upload_picture_3'] = SimpleUploadedFile(name='test_3.jpg', 
                    content=open('test_folder/test_file/test_3.jpg', 'rb').read(), content_type='image/jpg')
        teacher_post_data['upload_picture_4'] = SimpleUploadedFile(name='test_4.jpg', 
                    content=open('test_folder/test_file/test_4.jpg', 'rb').read(), content_type='image/jpg')
        teacher_post_data['upload_picture_5'] = SimpleUploadedFile(name='test_5.jpg', 
                    content=open('test_folder/test_file/test_5.jpg', 'rb').read(), content_type='image/jpg')
        
        # 用這個寫法的話好像不能一次 測試五張圖所以捨棄改用上面的做法
        #with open('test_folder/test_file/test_1.jpg','rb') as test_pic :
            # had to include 'rb' when opening the image
        #    teacher_post_data['upload_picture_1'] = test_pic
        #    self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建立老師,看看目的資料夾是否有出現該檔案?
        self.assertEqual(os.path.isfile('user_upload/teachers/test_teacher2@test.com/user_info/test_1.jpg'), True)
        self.assertEqual(os.path.isfile('user_upload/teachers/test_teacher2@test.com/user_info/test_1.jpeg'), True)
        # 除了1以外其他測試 轉化過的 jpeg就好
        self.assertEqual(os.path.isfile('user_upload/teachers/test_teacher2@test.com/user_info/test_2.jpeg'), True)
        self.assertEqual(os.path.isfile('user_upload/teachers/test_teacher2@test.com/user_info/test_3.jpeg'), True)
        self.assertEqual(os.path.isfile('user_upload/teachers/test_teacher2@test.com/user_info/test_4.jpeg'), True)
        self.assertEqual(os.path.isfile('user_upload/teachers/test_teacher2@test.com/user_info/test_5.jpeg'), True)
        # 檢查路徑是否正確寫入老師資料
        teacher_obj = teacher_profile.objects.get(username = 'test_teacher2@test.com')
        self.assertEqual(teacher_obj.upload_picture_1_location, 
            '/user_upload/teachers/test_teacher2@test.com/user_info/test_1.jpeg')
        self.assertEqual(teacher_obj.upload_picture_2_location, 
            '/user_upload/teachers/test_teacher2@test.com/user_info/test_2.jpeg')
        self.assertEqual(teacher_obj.upload_picture_3_location, 
            '/user_upload/teachers/test_teacher2@test.com/user_info/test_3.jpeg')
        self.assertEqual(teacher_obj.upload_picture_4_location, 
            '/user_upload/teachers/test_teacher2@test.com/user_info/test_4.jpeg')
        self.assertEqual(teacher_obj.upload_picture_5_location, 
            '/user_upload/teachers/test_teacher2@test.com/user_info/test_5.jpeg')


        # 測試結束,把老師的資料夾砍掉
        try:
            shutil.rmtree('user_upload/teachers/' + 'test_teacher2@test.com')
        except:
            pass
    
    @skip
    def test_return_teacher_profile_for_public_pic_and_url(self):
        '''當老師有上傳圖片時,要返回資料,公開頁的資訊'''
        pass
        t_obj = teacher_profile.objects.get(id=1)
        
    @skip
    def test_return_teacher_profile_for_self_looking_pic_and_url(self):
        '''當老師有上傳圖片時,要返回資料,給自己看的資訊'''
        pass
    @skip
    def test_teacher_edit_profile_for_upload_pic_and_url(self):
        '''當老師在會員中心編輯資料、新上傳圖片'''
        pass
    @skip
    def test_teacher_edit_profile_for_delete_pic_and_url(self):
        '''當老師在會員中心編輯資料、刪除原本上傳的圖片'''
        pass
    
    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name1)
        except:
            pass

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
        if settings.DISABLED_EMAIL == False:
            self.assertEqual(mail.outbox[0].subject, '[副本]Quikok!開課 註冊成功通知')

    
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
        row_thumbnail_pic_path = 'user_upload/temp/before_signed_up/tamio0800111111/customized_lesson_background.png'
        picture_in_binary = open(row_thumbnail_pic_path, 'rb')
        teacher_post_data['upload_snapshot'] = picture_in_binary

        self.assertNotIn(
            'thumbnail',
            teacher_profile.objects.filter(username=test_username).first().thumbnail_dir,
        )  # 在還沒有更新前，應該沒有大頭貼

        response = client.post(path='/api/account/editTeacherProfile/', data=teacher_post_data)
        
        
        #self.assertEqual(
        #    os.path.getsize(row_thumbnail_pic_path),
        #    os.path.getsize(teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:]),
        #    teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:]
        #)  #更新後，兩個大頭貼應該一樣了 >> 因為現在會縮圖，所以不能這樣看
        self.assertGreaterEqual(
            os.path.getsize(row_thumbnail_pic_path),
            os.path.getsize(teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:]),
            teacher_profile.objects.filter(username=test_username).first().thumbnail_dir[1:]
        )
        
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
        self.test_username2 = 'test_student_username2@test.com'
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
            shutil.rmtree('user_upload/students/' + self.test_username2)
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
    
    
    @skip
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
            open('user_upload/temp/before_signed_up/tamio0800111111/customized_lesson_background.png', 'rb')
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
                f'/user_upload/students/{self.test_username}/thumbnail.jpeg',  # 因為會縮圖
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


    def test_return_student_profile_for_public_viewing_work(self):
        student_post_data = {
            'regEmail': self.test_username,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regNickname': 'test_student_nickname',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        get_student_info_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id
        }
        response = \
            self.client.get(path='/api/account/returnStudentProfileForPublicViewing/', data=get_student_info_post_data)

        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"nickname": "test_student_nickname"', str(response.content, "utf8"))
        self.assertIn('"is_male": true', str(response.content, "utf8"))
        self.assertIn(f'"upload_snapshot": {student_profile.objects.get(id=1).thumbnail_dir}', str(response.content, "utf8"))

        # 註冊第二個學生，增加snapshot
        the_pic = open('user_upload/articles/default_main_picture.png', 'rb')
        student_post_data = {
            'regEmail': self.test_username2,
            'regPwd': '00000000',
            'regName': 'test_student_nam2e',
            'regNickname': '',
            'regBirth': '1990-12-25',
            'regGender': 0,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': '',
            'upload_snapshot': the_pic
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        get_student_info_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id
        }
        response = \
            self.client.get(path='/api/account/returnStudentProfileForPublicViewing/', data=get_student_info_post_data)

        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"nickname": "test_student_nam2e"', str(response.content, "utf8"))  # 因為沒輸入，所以是名字
        self.assertIn('"is_male": false', str(response.content, "utf8"))
        self.assertIn(f'"upload_snapshot": "{student_profile.objects.get(id=2).thumbnail_dir}"', str(response.content, "utf8"))


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


class SPEED_TESTS(TestCase):
    '''
    用來測試各式各樣的時間花費
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


    @skip
    def test_string_functions(self):
        n = 5000000
        x = 'dwerfwrfwefd'
        st1 = time()
        for _ in range(n):
            len(x)
        end1 = time()
        for _ in range(n):
            x == ''
        end2 = time()
        for _ in range(n):
            x in ['',]
        end3 = time()
        for _ in range(n):
            x != ''
        end4 = time()
        for _ in range(n):
            not x == ''
        end5 = time()

        '''
        len() takes 0.46376800537109375 seconds
        =='' takes 0.34960293769836426 seconds
        in takes 0.5897660255432129 seconds
        !='' takes 1.100010871887207 seconds
        not =='' takes 0.9897921085357666 seconds
        '''

        self.fail(f"\nlen() takes {end1-st1} seconds\n=='' takes {end2-end1} seconds\nin takes {end3-end2} seconds\n!='' takes {end4-end3} seconds\nnot =='' takes {end5-end4} seconds\n")


    @skip
    def test_comparasion_operators(self):
        n = 5000000
        x = True
        st1 = time()
        for _ in range(n):
            x == True
        end1 = time()
        for _ in range(n):
            x is True
        end2 = time()
        for _ in range(n):
            x != True
        end3 = time()
        for _ in range(n):
            x is not True
        end4 = time()
        '''
        == True takes 0.28649282455444336 seconds
        is True takes 0.24224424362182617 seconds
        != True takes 0.27544379234313965 seconds
        is not True takes 0.26437926292419434 seconds
        '''
        self.fail(f"\n== True takes {end1-st1} seconds\nis True takes {end2-end1} seconds\n!= True takes {end3-end2} seconds\nis not True takes {end4-end3} seconds\n")


    @skip
    def test_django_orm_query_speed(self):
        n = 5000
        end = time()
        t = teacher_profile.objects.get(id=1)
        for _ in range(n):
            teacher_profile.objects.get(id=1)
        end1 = time()
        for _ in range(n):
            teacher_profile.objects.filter(id=1).first()
        end2 = time()
        for _ in range(n):
            teacher_profile.objects.filter(id=1).exists()
        end3 = time()
        for _ in range(n):
            t.nickname
        end4 = time()
        for _ in range(n):
            teacher_profile.objects.get(Q(id=1))
        end5 = time()
        disc = f"\nget: {end1-end}\nfilter.first(): {end2-end1}\nexists: {end3-end2}\nquery_from_obj: {end4-end3}\nget_with_Q: {end5-end4}\n\n"
        
        '''
        get: 6.031943082809448
        filter.first(): 16.3274347782135
        exists: 4.141175985336304
        query_from_obj: 0.0011720657348632812
        get_with_Q: 7.71540904045105
        '''
        
        self.fail(disc)


    @skip
    def test_if_asyncio_faster_than_sync_in_creating_record(self):
        '''
        測試使用異步方式建立資料會不會比同步快，理論上是一定會啦，
        但我想知道異步function寫在同步的django views function中究竟會不會以異步來執行，
        同時如果可以的話，速度又會快多少。
        '''
        from asgiref.sync import sync_to_async

        # 使用異步寫入的方式，變成一筆都沒有進去，有沒有可能只是不能同時寫入，但可以同時讀取呢？
        # 來試試看先同步寫入再比較同步讀取 & 異步讀取。

        test_epochs = 50
        # 先建立50個epochs就好，免得等半天
        for i in range(test_epochs):
            teacher_post_data = {
                'regEmail': f"user_sync_test_{i}@gmail.com",
                'regPwd': '00000000',
                'regName': f'test_sync_name_{i}',
                'regNickname': f'test_nickname_{i}',
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
        print(f"{test_epochs} records have been created.")

        # 先嘗試同步讀取
        sync_results = list()
        sync_read_start_time = time()
        for i in range(test_epochs):
            teacher_object = \
                teacher_profile.objects.get(username = f"user_sync_test_{i}@gmail.com")
            sync_results.append(teacher_object.username)
        
        self.assertTrue(len(sync_results)==50, sync_results)
        print(f"sync_read_end_time: {time() - sync_read_start_time}")
        
        # 嘗試看看能不能異步讀取 >>  不行，要改寫ORM API，不然到了ORM還是要一步一步來
        # 嘗試看看能不能多線程讀取 >>  不行，sqlite不能同時讀取，但不曉得MySql可不可以
        # 呈上，是可以的，使用方法如下：
        '''
        async def async_read(id):
            teacher = \
                 await sync_to_async(teacher_profile.objects.filter(id=id).first)()
             print(f"Found teacher: {teacher is None} {id}.")
        
        tasks = [async_read(_) for _ in range(50)]
        asyncio.run(asyncio.wait(tasks))
        '''

        '''async_results = list()
        async def async_read(user_id):
            await sync_to_async(list)(
                teacher_profile.objects.get(username = f"user_async_test_{user_id}@gmail.com").username
                )
            teacher_object = \
                teacher_profile.objects.get(username = f"user_async_test_{user_id}@gmail.com")
            async_results.append(teacher_object.username)
        
        async_read_start_time = time()
        tasks = [async_read(_) for _ in range(test_epochs)]
        asyncio.run(asyncio.wait(tasks))
        
        self.assertTrue(len(async_results)==50, async_results)
        print(f"async_read_end_time: {time() - async_read_start_time}")'''
        
        '''thread_read_start_time = time()
        def thread_get_object(user_id):
            print(f"Getting teacher:{user_id}...")
            teacher_object = \
                teacher_profile.objects.get(username = f"user_async_test_{user_id}@gmail.com")
            print(f"Teacher\'s username: {teacher_object.username}...")

        # 使用多線程讀取看看
        for _ in range(50):
            threading.Thread(target=thread_get_object, args=(_,)).start()

        print(f"thread_read_end_time: {time() - thread_read_start_time}")'''


        
class Invitation_Code_Test(TestCase):
    '''
    測試邀請碼機制是否有成功建立的測試
    '''
    def setUp(self):
        self.client = Client()
        self.first_ic = "thisIsTheFirstIC"
        Group.objects.bulk_create(
            [
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ]
        )
        invitation_code_detail.objects.create(
            invitation_code=self.first_ic,
            detail="這是一個關於邀請碼的解釋",
        ).save()

        
    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name1)
        except:
            pass

    def test_invitation_code_tables_created(self):
        '''
        測試邀請碼相關的table已經建立起來了
        '''
        invitation_code_detail_cnt = \
            invitation_code_detail.objects.count()
        
        user_invitation_code_mapping_cnt = \
            user_invitation_code_mapping.objects.count()

        self.assertTrue(invitation_code_detail_cnt >= 0)
        self.assertTrue(user_invitation_code_mapping_cnt >= 0)


    def test_teacher_register_with_invitation_code(self):
        '''
        測試老師註冊時帶入註冊碼(非另一用戶邀請)
        '''
        self.test_teacher_name1 = 'test_teacher1_user@test.com'
        test_invitation_code = 'test0800'
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:1,2,3,4,5;4:1,2,3,4,5;',
            'invitation_code': test_invitation_code,  # 嘗試輸入邀請碼
        }
        response = \
            self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        self.assertIn('success', str(response.content, "utf8"))  # 註冊成功
        # 確認該老師是否有該邀請碼

        teacher_object = teacher_profile.objects.get(username=self.test_teacher_name1)
        self.assertEqual(teacher_object.mobile, teacher_post_data['regMobile'])

        self.assertEqual(invitation_code_detail.objects.count(), 1)  # 應該有一筆IC的資料

        teacher_inv_codes = \
            user_invitation_code_mapping.objects.values_list(
                'invitation_code', flat=True).filter(auth_id=teacher_object.auth_id)
        
        self.assertTrue(
            teacher_post_data['invitation_code'] in teacher_inv_codes,
            teacher_inv_codes)
        self.assertEqual(len(teacher_inv_codes), 1)
        self.assertEqual(
            user_invitation_code_mapping.objects.get(auth_id=teacher_object.auth_id).user_type,
            "teacher"
        )
        # 老師的註冊碼應該有被儲存起來


    def test_student_register_with_invitation_code(self):
        '''
        測試學生註冊時帶入註冊碼(非另一用戶邀請)
        '''
        self.test_student_name1 = 'test_student1_user@test.com'
        test_invitation_code = 'test0800'
        student_post_data = {
            'regEmail': self.test_student_name1,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': "",
            'invitation_code': test_invitation_code,
        }
        response = \
            self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        self.assertIn('success', str(response.content, "utf8"))  # 註冊成功
        # 確認該學生是否有該邀請碼

        student_object = student_profile.objects.get(username=self.test_student_name1)
        self.assertEqual(student_object.mobile, student_post_data['regMobile'])
        
        student_inv_codes = \
            user_invitation_code_mapping.objects.values_list(
                'invitation_code', flat=True).filter(auth_id=student_object.auth_id)
        
        self.assertTrue(
            student_post_data['invitation_code'] in student_inv_codes,
            student_inv_codes)
        self.assertEqual(len(student_inv_codes), 1)
        # 學生的註冊碼應該有被儲存起來


    def test_student_register_with_mandarin_invitation_code(self):
        '''
        測試學生註冊時帶入中文註冊碼(非另一用戶邀請)
        '''
        self.test_student_name1 = 'test_student1_user@test.com'
        test_invitation_code = '這是一段可愛的註冊碼'
        student_post_data = {
            'regEmail': self.test_student_name1,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': "",
            'invitation_code': test_invitation_code,
        }
        response = \
            self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        self.assertIn('success', str(response.content, "utf8"))  # 註冊成功
        # 確認該學生是否有該邀請碼
        student_object = student_profile.objects.get(username=self.test_student_name1)
        self.assertEqual(student_object.mobile, student_post_data['regMobile'])
        student_inv_codes = \
            user_invitation_code_mapping.objects.values_list(
                'invitation_code', flat=True).filter(auth_id=student_object.auth_id)
        
        self.assertTrue(
            student_post_data['invitation_code'] in student_inv_codes,
            student_inv_codes)
        self.assertEqual(len(student_inv_codes), 1)
        # 學生的註冊碼應該有被儲存起來

    
        

