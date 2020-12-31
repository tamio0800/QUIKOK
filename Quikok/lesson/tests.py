from django.test import RequestFactory, TestCase
from django.test import Client
import pandas as pd
import os
import shutil
from lesson import lesson_tools
from lesson.models import lesson_info_for_users_not_signed_up 
from lesson.models import lesson_info
from lesson.models import lesson_card
from lesson.models import lesson_sales_sets
from account.models import student_profile, teacher_profile
from account.models import specific_available_time
from django.contrib.auth.models import Permission, User, Group
from unittest import skip
from lesson.models import lesson_booking_info
from account_finance.models import student_remaining_minutes_of_each_purchased_lesson_set


# python manage.py test lesson/ --settings=Quikok.settings_for_test
class Lesson_Info_Related_Functions_Test(TestCase):
 
    def test_before_signing_up_create_or_edit_a_lesson_exist(self):
        # 測試這個函式是否存在，並且應該回傳status='success', errCode=None, errMsg=None
        # self.factory = RequestFactory()
        self.client = Client()
        response = self.client.post(path='/api/lesson/beforeSigningUpCreateOrEditLesson/')
        self.assertEqual(response.status_code, 200)
        

    def test_before_signing_up_create_or_edit_a_lesson_received_argument(self):
        # 測試這個函式能不能接受到自訂的「dummy_teacher_id」參數
        self.client = Client()
        response = self.client.post(
            path='/api/lesson/beforeSigningUpCreateOrEditLesson/',
            data={'dummy_teacher_id': 'tamio080011111'})
        print(str(response.content, encoding='utf8'))
        
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1
            }
        )


    def test_saving_and_retreiving_data_from_db(self):
        # 測試這個函式能不能將資料寫入資料庫
        new_added_lesson = \
            lesson_info_for_users_not_signed_up.objects.create(
                big_title='test',
                little_title='test',
                title_color='#fffffff',
                background_picture_code=3,
                background_picture_path='',
                lesson_title='test',
                price_per_hour=300,
                lesson_has_one_hour_package=True,
                trial_class_price=100,
                highlight_1='test',
                highlight_2='test',
                highlight_3='test',
                lesson_intro='test',
                how_does_lesson_go='test',
                target_students='test',
                lesson_remarks='test',
                syllabus='test',
                lesson_attributes='test',
                dummy_teacher_id='tamio0800111111'
            )
        print(new_added_lesson.id)
        new_added_lesson.save()

        self.assertEqual(
            lesson_info_for_users_not_signed_up.objects.all().count(),
            1,
            lesson_info_for_users_not_signed_up.objects.values()
        )


    def test_saving_data_through_before_signing_up_create_or_edit_a_lesson(self):
        # 測試這個函式能不能通過before_signing_up_create_or_edit_a_lesson函式，
        # 使用預設的背景圖，將資料寫入資料庫。
        self.client = Client()
        arguments_dict = dict()

        arguments_dict = {
            'dummy_teacher_id': 'tamio0800111111',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 3,
            'background_picture_path': '',
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
        
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1
            }
        )


    def test_saving_data_through_before_signing_up_create_or_edit_a_lesson_with_self_set_background_picture(self):
        # 測試這個函式能不能通過before_signing_up_create_or_edit_a_lesson函式，
        # 使用用戶自訂的背景圖，將資料寫入資料庫。
        self.client = Client()
        arguments_dict = dict()

        dummy_teacher_id = 'tamio0800111111'
        background_picture = open('user_upload/temp/before_signed_up/tamio0800111111/customized_lesson_background.jpg', 'rb')
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

        # 圖片應該會被上傳，並且暫存在 user_upload/temp/before_signed_up/{dummy_teacher_id}/ 內
        # 並且改名為 customized_background_picture

        self.assertEqual(
            os.path.isdir(f'user_upload/temp/before_signed_up/{dummy_teacher_id}'),
            True,
            os.listdir('user_upload/temp/before_signed_up')
        )  # 確認有建立該資料夾

        self.assertEqual(
            'customized_lesson_background' in os.listdir(f'user_upload/temp/before_signed_up/{dummy_teacher_id}')[0],
            True,
            os.listdir(f'user_upload/temp/before_signed_up/{dummy_teacher_id}')
        )  # 確認該資料夾裡面有背景照片

        # 清理產出的測試檔案
        #try:
        #    shutil.rmtree(f'user_upload/temp/before_signed_up/{dummy_teacher_id}')
        #except Exception as e:
        #    print(f'Something went wrong:  {e}')
        
        # print(lesson_info_for_users_not_signed_up.objects.values())
        
        self.assertEqual(
            lesson_info_for_users_not_signed_up.objects.filter().first().dummy_teacher_id,
            dummy_teacher_id,
            lesson_info_for_users_not_signed_up.objects.values()
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


    def test_lesson_card_syncronized_after_creating_a_lesson(self):
        '''
        測試創建課程後，課程小卡也會同步出現正確的資料
        '''
        self.client = Client()

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

        test_username = 'test201218_teacher_user@test.com'
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            True
        )
        # 應該已經建立完成了

        lesson_post_data = {
            'userID': 1,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 800,
            'discount_price': '10:90;20:80;30:75;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': 69,
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
                path='/api/lesson/createOrEditLesson/',
                data=lesson_post_data)
        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')
        
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1
            }
        )

        # 測試課程有寫入
        self.assertEqual(
            (
                lesson_info.objects.filter(id=1).first().big_title,
                lesson_info.objects.filter(id=1).first().little_title,
                lesson_info.objects.filter(id=1).first().lesson_title,
                lesson_info.objects.filter(id=1).first().price_per_hour
            ),
            (
                lesson_post_data['big_title'],
                lesson_post_data['little_title'],
                lesson_post_data['lesson_title'],
                lesson_post_data['price_per_hour']
            )
        )

        # 測試課程小卡有寫入
        self.assertEqual(
            (
                lesson_card.objects.filter(id=1).first().teacher_nickname,
                lesson_card.objects.filter(id=1).first().education,
                lesson_card.objects.filter(id=1).first().working_experience,
                lesson_card.objects.filter(id=1).first().big_title,
                lesson_card.objects.filter(id=1).first().little_title,
                lesson_card.objects.filter(id=1).first().lesson_title,
                lesson_card.objects.filter(id=1).first().price_per_hour
            ),
            (
                teacher_post_data['regNickname'],
                teacher_post_data['education_1'],
                teacher_post_data['company'],
                lesson_post_data['big_title'],
                lesson_post_data['little_title'],
                lesson_post_data['lesson_title'],
                lesson_post_data['price_per_hour']
            ),
            lesson_card.objects.values()
        )

        
    def test_lesson_card_syncronized_after_editting_a_lesson(self):
        '''
        測試創建課程後、再進行編輯，課程小卡也會同步出現正確的資料
        '''
        self.client = Client()

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

        test_username = 'test201218_teacher_user@test.com'
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            True
        )
        # 應該已經建立完成了

        lesson_post_data = {
            'userID': 1,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 800,
            'discount_price': '10:90;20:80;30:75;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': 69,
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
                path='/api/lesson/createOrEditLesson/',
                data=lesson_post_data)
        
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
            (
                lesson_info.objects.filter(id=1).first().big_title,
                lesson_info.objects.filter(id=1).first().little_title,
                lesson_info.objects.filter(id=1).first().lesson_title,
                lesson_info.objects.filter(id=1).first().price_per_hour
            ),
            (
                lesson_post_data['big_title'],
                lesson_post_data['little_title'],
                lesson_post_data['lesson_title'],
                lesson_post_data['price_per_hour']
            )
        )

        '''
        截止以上為止，都是舊的測試，代表課程可以順利建立，且同步到課程小卡，
        接下來要修改剛剛建立的課程，看看課程小卡有沒有被同步。
        '''
        lesson_post_data['big_title'] = '第二次的測試標題'
        lesson_post_data['little_title'] = '第二次的測試小標題'
        lesson_post_data['lesson_title'] = '課程主標題標題'
        lesson_post_data['price_per_hour'] = 1200
        lesson_post_data['action'] = 'editLesson'
        lesson_post_data['lessonID'] = 1

        response = \
            self.client.post(
                path='/api/lesson/createOrEditLesson/',
                data=lesson_post_data)

        self.assertIn(
            'success', str(response.content, encoding='utf8'),
            str(response.content, encoding='utf8')
        )


        # 測試課程小卡有寫入
        self.assertEqual(
            (
                lesson_card.objects.filter(id=1).first().big_title,
                lesson_card.objects.filter(id=1).first().little_title,
                lesson_card.objects.filter(id=1).first().lesson_title,
                lesson_card.objects.filter(id=1).first().price_per_hour
            ),
            (
                lesson_post_data['big_title'],
                lesson_post_data['little_title'],
                lesson_post_data['lesson_title'],
                lesson_post_data['price_per_hour']
            ),
            lesson_card.objects.values()
        )

        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')

  
    def test_lesson_card_syncronized_after_editting_teacher_profile(self):
        '''
        測試創建課程後、再編輯老師的個人資料，課程小卡也會同步出現正確的資料
        '''
        self.client = Client()

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

        test_username = 'test201218_teacher_user@test.com'
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            True
        )
        # 應該已經建立完成了

        lesson_post_data = {
            'userID': 1,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 800,
            'discount_price': '10:90;20:80;30:75;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': 69,
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
                path='/api/lesson/createOrEditLesson/',
                data=lesson_post_data)
        # 建立新課程
        
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1
            }
        )  # 建立新課程成功

        self.assertEqual(
            lesson_card.objects.count(),
            1,
            lesson_card.objects.values()
          )  # 課程小卡成功連動建立

        self.assertEqual(
            (
                lesson_info.objects.filter(id=1).first().big_title,
                lesson_info.objects.filter(id=1).first().little_title,
                lesson_info.objects.filter(id=1).first().lesson_title,
                lesson_info.objects.filter(id=1).first().price_per_hour
            ),
            (
                lesson_post_data['big_title'],
                lesson_post_data['little_title'],
                lesson_post_data['lesson_title'],
                lesson_post_data['price_per_hour']
            )
        ) 

        '''
        截止以上為止，都是舊的測試，代表課程可以順利建立，且同步到課程小卡，
        接下來要修改剛剛建立的老師資訊，看看課程小卡有沒有被同步。
        '''

        teacher_post_data['userID'] = 1
        teacher_post_data['nickname'] = '新的暱稱啦'
        teacher_post_data['education_1'] = '新的教育程度'
        teacher_post_data['company'] = '新的工作經驗'
        teacher_post_data['intro'] = '新的自我介紹歐耶'
        teacher_post_data['mobile'] = '0911-222345'
        teacher_post_data['teacher_general_availabale_time'] = '0:1,2,3,4,5;5:6,7,8,9,10;3:10,11,12;'

        # 將老師的修改資料傳到對應的api
        response = \
            self.client.post(
                path='/api/account/editTeacherProfile/',
                data=teacher_post_data)  # 老師修改個人資料

        print(f'str(response.content, encoding=utf8)  {str(response.content, encoding="utf8")}')
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
            },
            str(response.content, encoding='utf8')
        )  # 老師修改個人資料成功

        # 測試課程小卡有寫入
        self.assertEqual(
            (
                lesson_card.objects.filter(teacher_auth_id=1).first().teacher_nickname,
                lesson_card.objects.filter(teacher_auth_id=1).first().education,
                lesson_card.objects.filter(teacher_auth_id=1).first().working_experience,
            ),
            (
                teacher_post_data['nickname'],
                teacher_post_data['education_1'],
                teacher_post_data['company'],
            ),
            lesson_card.objects.values()
        )  # 測試課程小卡有寫入

        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')


    def test_sales_set_update_after_creating_a_lesson(self):
        
        self.client = Client()
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

        test_username = 'test201218_teacher_user@test.com'
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        self.assertEqual(
            os.path.isdir('user_upload/teachers/' + test_username),
            True
        )
        # 應該已經建立完成了

        lesson_post_data = {
            'userID': 1,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 800,
            'discount_price': '10:90;20:80;30:75;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': 69,
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
                path='/api/lesson/createOrEditLesson/',
                data=lesson_post_data)
        # 建立完課程了

        # 接下來測試看看課程小卡有沒有連動更改
        all_lesson_1_sales_sets = \
            list(lesson_sales_sets.objects.filter(lesson_id=1).values_list('sales_set', flat=True))
        
        # print(f'lesson_info.objects.values():  {lesson_info.objects.values()}')
        # 因為上方有 "試課優惠"，且也有 "單堂方案"，故應該有:
        #   trial、no_discount、10:90、20:80、30:75  這五種 sales_sets
        self.assertListEqual(
            ['trial', 'no_discount', '10:90', '20:80', '30:75'],
            all_lesson_1_sales_sets,
            lesson_sales_sets.objects.values()
        )

        # 接下來測試價格計算對不對
        self.assertEqual(
            (
                lesson_post_data['price_per_hour'],
                round(lesson_post_data['price_per_hour'] * 0.9),
                round(lesson_post_data['price_per_hour'] * 0.8),
                round(lesson_post_data['price_per_hour'] * 0.75),
                round(lesson_post_data['price_per_hour'] * 0.75 * 30),
                lesson_post_data['trial_class_price'],
                10,
                0,
                True,
                True
            ),
            (
                lesson_sales_sets.objects.filter(sales_set='no_discount').first().price_per_hour_after_discount,
                lesson_sales_sets.objects.filter(sales_set='10:90').first().price_per_hour_after_discount,
                lesson_sales_sets.objects.filter(sales_set='20:80').first().price_per_hour_after_discount,
                lesson_sales_sets.objects.filter(sales_set='30:75').first().price_per_hour_after_discount,
                lesson_sales_sets.objects.filter(sales_set='30:75').first().total_amount_of_the_sales_set,
                lesson_sales_sets.objects.filter(sales_set='trial').first().price_per_hour_after_discount,
                lesson_sales_sets.objects.filter(sales_set='10:90').first().total_hours_of_the_sales_set,
                lesson_sales_sets.objects.filter(sales_set='10:90').first().taking_lesson_volume,
                lesson_sales_sets.objects.filter(sales_set='no_discount').first().is_open,
                lesson_sales_sets.objects.filter(sales_set='30:75').first().is_open,
            )
        )
        
        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')


    def test_sales_set_update_after_editting_a_lesson(self):
        
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
        test_username = 'test_teacher_user@test.com'
        try:
            shutil.rmtree('user_upload/teachers/' + test_username)
        except:
            pass
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;'
        }
        response = client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        self.assertIn(
            'success',
            str(response.content, 'utf8'),
        )

        # 應該已經建立完成了
        lesson_post_data = {
            'userID': 1,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 800,
            'discount_price': '10:90;20:80;30:75;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': 69,
            'highlight_1': 'test',
            'highlight_2': 'test',
            'highlight_3': 'test',
            'lesson_intro': 'test_lesson_intro',
            'how_does_lesson_go': 'test',
            'target_students': 'test',
            'lesson_remarks': 'test',
            'syllabus': 'test',
            'lesson_attributes': 'test'      
            }
        response = \
            client.post(path='/api/lesson/createOrEditLesson/', data=lesson_post_data)
        # 建立完課程了

        # 接下來要修改課程
        lesson_post_data['action'] = 'editLesson'
        lesson_post_data['lessonID'] = 1  # 因為是課程編輯，所以需要給課程的id
        lesson_post_data['little_title'] = '新的圖片小標題'
        lesson_post_data['lesson_title'] = '新的課程標題'
        lesson_post_data['price_per_hour'] = 1230
        lesson_post_data['trial_class_price'] = -999  # 不試教了
        lesson_post_data['discount_price'] = '5:95;10:90;50:70;'
        lesson_post_data['lesson_has_one_hour_package'] = False  # 也沒有單堂販賣了
        lesson_post_data['lesson_intro'] = 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Repudiandae, saepe itaque iste explicabo voluptas consectetur aliquam reiciendis magni expedita blanditiis minus temporibus facilis quod, dolorem, eligendi soluta! Ea, voluptate hic?'

        response = \
            client.post(path='/api/lesson/createOrEditLesson/', data=lesson_post_data)
        
        self.assertIn(
            'success',
            str(response.content, 'utf8'),
            (
                teacher_profile.objects.values(),
                lesson_info.objects.values()
            )
        )
        '''
        理論上這時該課程的 sales_sets 會存有 8 個 rows：
            non-active的:
                1. trial
                2. no_discount
                3. 10:90
                4. 20:80
                5. 30:75
            active的:
                1. 5:95
                2. 10:90
                3. 50:70
        '''
        self.assertEqual(
            (
                lesson_post_data['price_per_hour'],
                lesson_post_data['little_title'],
                lesson_post_data['trial_class_price'],
                lesson_post_data['discount_price'],
                lesson_post_data['lesson_intro']
            ),
            (
                lesson_info.objects.filter(id=1).first().price_per_hour,
                lesson_info.objects.filter(id=1).first().little_title,
                lesson_info.objects.filter(id=1).first().trial_class_price,
                lesson_info.objects.filter(id=1).first().discount_price,
                lesson_info.objects.filter(id=1).first().lesson_intro,
            ),
            lesson_info.objects.values()
        )

        self.assertEqual(
            8, lesson_sales_sets.objects.count(),
            (
                lesson_sales_sets.objects.values_list('sales_set', flat=True),
                lesson_sales_sets.objects.values_list('is_open', flat=True)
            )
        )

        self.assertEqual(
            5, lesson_sales_sets.objects.filter(is_open=False).count(),
        )
        self.assertEqual(
            3, lesson_sales_sets.objects.filter(is_open=True).count(),
        )
        self.assertListEqual(
            ['5:95', '10:90', '50:70'],
            list(lesson_sales_sets.objects.values_list('sales_set', flat=True).filter(is_open=True))
        )

        self.assertEqual(
            (
                round(lesson_post_data['price_per_hour'] * 0.7),
                round(lesson_post_data['price_per_hour'] * 50 * 0.7),
            ),
            (
                lesson_sales_sets.objects.filter(is_open=True).filter(sales_set='50:70').first().price_per_hour_after_discount,
                lesson_sales_sets.objects.filter(is_open=True).filter(sales_set='50:70').first().total_amount_of_the_sales_set,
            )
        )

        lesson_post_data['selling_status'] = 'draft'
        response = \
            client.post(path='/api/lesson/createOrEditLesson/', data=lesson_post_data)
        # 將課程改為暫存測試
        self.assertIn(
            'success',
            str(response.content, 'utf8'),
            (
                teacher_profile.objects.values(),
                lesson_info.objects.values()
            )
        )
        self.assertEqual(
            8, lesson_sales_sets.objects.count(),
            (
                lesson_sales_sets.objects.values_list('sales_set', flat=True),
                lesson_sales_sets.objects.values_list('is_open', flat=True)
            )
        )
        self.assertEqual(
            8, lesson_sales_sets.objects.filter(is_open=False).count(),
        )


        try:
            shutil.rmtree(f'user_upload/teachers/{test_username}')
        except Exception as e:
            print(f'Error:  {e}')


class Lesson_Info_Test(TestCase):

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
        self.test_username = 'test_teacher_user@test.com'
        teacher_post_data = {
            'regEmail': self.test_username,
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
        self.test_student_name = 'test_student@a.com'
        student_post_data = {
            'regEmail': self.test_student_name,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        # 建立課程
        lesson_post_data = {
            'userID': 1,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 800,
            'discount_price': '10:90;20:80;30:75;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': 69,
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
        self.client.post(path='/api/lesson/createOrEditLesson/', data=lesson_post_data)

        # 先取得兩個可預約日期，避免hard coded未來出錯
        # 時段我都設1,2,3,4,5，所以只要在其中就ok
        self.available_date_1 = specific_available_time.objects.filter(id=1).first().date
        self.available_date_2 = specific_available_time.objects.filter(id=2).first().date
        self.available_date_3 = specific_available_time.objects.filter(id=3).first().date
        self.available_date_4 = specific_available_time.objects.filter(id=4).first().date
        self.available_date_5 = specific_available_time.objects.filter(id=5).first().date
    
    
    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name)
            shutil.rmtree('user_upload/teachers/' + self.test_username)
        except:
            pass


    def test_if_return_lesson_details_for_browsing_works(self):
        
        browsing_post_data = {
            'action': 'browsing',
            'lessonID': lesson_info.objects.first().id,
            'userID': student_profile.objects.first().auth_id
        }
        response = self.client.get(path='/api/lesson/returnLessonDetailsForBrowsing/', data=browsing_post_data)

        print(f"for_browsing str(response.content, 'utf8')  {str(response.content, 'utf8')}")
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))
        self.assertIn(teacher_profile.objects.first().nickname, str(response.content, 'utf8'))
        





class Lesson_Booking_Related_Functions_Test(TestCase):

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
        self.test_username = 'test_teacher_user@test.com'
        teacher_post_data = {
            'regEmail': self.test_username,
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
        self.test_student_name = 'test_student@a.com'
        student_post_data = {
            'regEmail': self.test_student_name,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        # 建立課程
        lesson_post_data = {
            'userID': 1,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 800,
            'discount_price': '10:90;20:80;30:75;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': 69,
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
        self.client.post(path='/api/lesson/createOrEditLesson/', data=lesson_post_data)

        # 先取得兩個可預約日期，避免hard coded未來出錯
        # 時段我都設1,2,3,4,5，所以只要在其中就ok
        self.available_date_1 = specific_available_time.objects.filter(id=1).first().date
        self.available_date_2 = specific_available_time.objects.filter(id=2).first().date
        self.available_date_3 = specific_available_time.objects.filter(id=3).first().date
        self.available_date_4 = specific_available_time.objects.filter(id=4).first().date
        self.available_date_5 = specific_available_time.objects.filter(id=5).first().date


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name)
            shutil.rmtree('user_upload/teachers/' + self.test_username)
        except:
            pass


    def test_if_get_lesson_specific_available_time_works_properly(self):

        query_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1
            }

        response = self.client.post(
            path='/api/lesson/getLessonSpecificAvailableTime/',
            data=query_post_data
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn('success', str(response.content, 'utf8'))
        # print(f"raw response.content: {str(response.content, 'utf8')}")

        # 接下來來隨機調整一些時段，讓它們變成 is_occupied ，看能不能正常產出
        the_specific_available_time_objects = \
            specific_available_time.objects.filter(teacher_model=teacher_profile.objects.first())
        
        temp_obj = the_specific_available_time_objects.filter(id=4).first()
        temp_obj.is_occupied = True
        temp_obj.save()
        temp_obj = the_specific_available_time_objects.filter(id=14).first()
        temp_obj.is_occupied = True
        temp_obj.save()
        
        response = self.client.post(
            path='/api/lesson/getLessonSpecificAvailableTime/',
            data=query_post_data
            )
        
        self.assertIn('success', str(response.content, 'utf8'))
        self.assertNotIn('"bookedTime": []', str(response.content, 'utf8')) # 理論上不會是空的了
        # print(f"editted response.content: {str(response.content, 'utf8')}")

    
    def test_if_booking_lessons_received_data(self):
        # 確認這個函式收得到參數
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 60
        ).save()  # 建立一個試教 set

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:1,2;'
            }

        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data
            )

        self.assertEqual(response.status_code, 200)

    
    def test_if_booking_lessons_check_students_available_remaining_minutes(self):
        # 測試預約前會檢查學生剩餘時數
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 60
        ).save()  # 建立一個試教 set
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.count(), 1,
        student_remaining_minutes_of_each_purchased_lesson_set.objects.values())
        #print(f'student_remaining_minutes_of_each_purchased_lesson_set.objects.values(), \
        #{student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:1,2;'
        }  # 只預約一小時 >> ok

        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)

        self.assertIn('success', str(response.content, 'utf8'))
        
        the_available_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first()
        the_available_remaining_minutes_object.available_remaining_minutes = 60
        the_available_remaining_minutes_object.save()  # 重建 60 分鐘的額度

        self.assertEqual(
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().available_remaining_minutes,
            60,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )

        booking_post_data['bookingDateTime'] = f'{self.available_date_1}:2;{self.available_date_2}:4;'
        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  
        # 只預約一小時 >> ok

        the_available_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first()
        the_available_remaining_minutes_object.available_remaining_minutes = 60
        the_available_remaining_minutes_object.save()  # 重建 60 分鐘的額度

        self.assertIn('success', str(response.content, 'utf8'))

        booking_post_data['bookingDateTime'] = f'{self.available_date_1}:2,3;{self.available_date_2}:4;'
        # print(f"booking_post_data['bookingDateTime'] {booking_post_data['bookingDateTime']}")
        # 預約了1.5小時，超過1小時的額度 >> rejected

        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  

        self.assertIn('failed', str(response.content, 'utf8'))
        #print(f'response.content:  {str(response.content, "utf8")}')

        booking_post_data['bookingDateTime'] = ''
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  
        # 沒有回傳時段，應該會是錯誤
        self.assertIn('failed', str(response.content, 'utf8'))

        booking_post_data['bookingDateTime'] = f'{self.available_date_1}:;{self.available_date_2}:4,5;'
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  
        self.assertIn('success', str(response.content, 'utf8'))

        the_available_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first()
        the_available_remaining_minutes_object.available_remaining_minutes = 150
        the_available_remaining_minutes_object.save()  # 重建 150 分鐘的額度

        booking_post_data['bookingDateTime'] = f'{self.available_date_1}:;{self.available_date_2}:1,2,3,4,5;'
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  
        self.assertIn('failed', str(response.content, 'utf8'))
        # 因為是試教，最多只能預約2堂課(1小時)


    def test_if_booking_trial_lessons_modified_remaining_minutes_after_booking_successfully(self):
        '''
        這個測試用在檢查：當試教預約成功後，是否有從學生那邊扣除剩餘時數，並進行對應的資料庫更新。
        '''
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 60  
        ).save()  # 建立一個試教 set
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:3;'
        }  # 即使只預約一堂，都應該全部扣除
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'))
        self.assertEqual(0,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().available_remaining_minutes)
        self.assertEqual(60,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().withholding_minutes)
        print(f'student_remaining_minutes_of_each_purchased_lesson_set1: \
            {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        self.assertEqual(
            (
                lesson_booking_info.objects.count(),
                lesson_booking_info.objects.first().teacher_auth_id,
                lesson_booking_info.objects.first().student_auth_id,
                lesson_booking_info.objects.first().booked_by,
                lesson_booking_info.objects.first().booking_set_id,
                lesson_booking_info.objects.first().booking_date_and_time,
                lesson_booking_info.objects.first().remaining_minutes
            ),
            (
                1,
                teacher_profile.objects.first().auth_id,
                student_profile.objects.first().auth_id,
                'student',
                lesson_sales_sets.objects.filter(
                    teacher_auth_id=teacher_profile.objects.first().auth_id,
                    sales_set='trial',
                    is_open=True
                ).first().id,
                f'{self.available_date_1}:3;',
                0
            ),
            lesson_booking_info.objects.values()
        )  # 測試 booking_info 有沒有成功建立

        student_remaining_minutes_of_each_purchased_lesson_set.objects.first().delete()
        lesson_booking_info.objects.first().delete()
        # 重建一個 60min 的試教
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 60  
        ).save()
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:3;{self.available_date_3}:1;'
        }  # 預約兩堂
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'))
        self.assertEqual(0,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().available_remaining_minutes)
        self.assertEqual(60,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().withholding_minutes)
        print(f'student_remaining_minutes_of_each_purchased_lesson_set2: \
            {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        self.assertEqual(
            (
                lesson_booking_info.objects.count(),
                lesson_booking_info.objects.first().teacher_auth_id,
                lesson_booking_info.objects.first().student_auth_id,
                lesson_booking_info.objects.first().booked_by,
                lesson_booking_info.objects.first().booking_set_id,
                lesson_booking_info.objects.first().booking_date_and_time,
                lesson_booking_info.objects.first().remaining_minutes
            ),
            (
                1,
                teacher_profile.objects.first().auth_id,
                student_profile.objects.first().auth_id,
                'student',
                lesson_sales_sets.objects.filter(
                    teacher_auth_id=teacher_profile.objects.first().auth_id,
                    sales_set='trial',
                    is_open=True
                ).first().id,
                f'{self.available_date_1}:3;{self.available_date_3}:1;',
                0
            ),
            lesson_booking_info.objects.values()
        )  # 測試 booking_info 有沒有成功建立

        student_remaining_minutes_of_each_purchased_lesson_set.objects.first().delete()
        lesson_booking_info.objects.first().delete()
        # 重建一個 60min 的試教
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 60  
        ).save()
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:3;{self.available_date_3}:1,2;'
        }  # 預約三堂，應該要失敗
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('failed', str(response.content, 'utf8'))
        self.assertIn('"errCode": "5"', str(response.content, 'utf8'))
        self.assertEqual(60,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().available_remaining_minutes)
        self.assertEqual(0,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().withholding_minutes)
        print(f'student_remaining_minutes_of_each_purchased_lesson_set3: \
            {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        self.assertEqual(lesson_booking_info.objects.count(), 0)

        # 接著嘗試建立一般的set，測試是否在還有試教方案前，不能進行一般預約

        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 10*60
        ).save()  # 建立一個 10:90 set

        self.assertEqual(2,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.count())
        # 應該要有兩個已購買方案了
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:3;{self.available_date_3}:1,2;'
        }  # 預約三堂，應該要失敗，因為目前有未動用試教方案，而試教要先使用
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('failed', str(response.content, 'utf8'))
        self.assertIn('"errCode": "5"', str(response.content, 'utf8'))

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_3}:1,2;'
        }  # 預約兩堂，應該要成功
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'), booking_post_data)
        self.assertEqual(0,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().available_remaining_minutes)
        self.assertEqual(60,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().withholding_minutes)
        print(f'student_remaining_minutes_of_each_purchased_lesson_set4  \
            {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')


    def test_if_booking_common_lessons_modified_remaining_minutes_after_booking_successfully(self):
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 60  
        ).save()  # 先建立一個試教 set
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 600
        ).save()  # 再建立一個 10:90 set
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.count(), 2)
        
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:3;{self.available_date_4}:1;'
        }  # 即使只預約一堂，都應該全部扣除
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))
        # 此時試教額度應該已經用完了

        # 來進行 10:90 的預約
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:1,2,3,4,5;{self.available_date_3}:1,2,3,5;'
        }  # 預約9個時段，合計270分鐘
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))
        print(f"str(response.content, 'utf8')  {str(response.content, 'utf8')}")
        print(lesson_booking_info.objects.values().filter(id=2))
        self.assertEqual(
            (
                270,
                330,
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_set_id=lesson_sales_sets.objects.filter(
                        teacher_auth_id=teacher_profile.objects.first().auth_id,
                        sales_set='10:90'
                    ).first().id
                ).first().withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_set_id=lesson_sales_sets.objects.filter(
                        teacher_auth_id=teacher_profile.objects.first().auth_id,
                        sales_set='10:90'
                    ).first().id
                ).first().available_remaining_minutes,
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values())
            # 測試預扣時數與可動用時數是否正確


    def test_if_booking_common_lessons_with_multiple_available_sets_work(self):
        '''
        這個測試的用意是，當本次預約需要用到複數個課程方案時，亦能成功執行。
        舉例來說，假設有兩個sets分別剩餘25分、100分，預約了120分鐘後，應該分別變成0分、5分。
        '''
        student_remaining_minutes_1 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 20)
        student_remaining_minutes_1.save()  # 建立一個 10:90 set，只有 20 分鐘
        student_remaining_minutes_2 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 90)
        student_remaining_minutes_2.save()  # 建立一個 10:90 set，只有 90 分鐘  # 再建立一個 10:90 set，只有 90 分鐘
        student_remaining_minutes_3 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='30:75').filter(is_open=True).first().id,
            available_remaining_minutes = 30*60)
        student_remaining_minutes_3.save()  # 再建立一個 30:75 set，有 1800 分鐘
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.count(), 3)

        # 來進行一個大預約
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:1,2,3,4,5;{self.available_date_2}:1,2,3,4,5;{self.available_date_3}:1,2,3,4,5;{self.available_date_4}:1,2,3,4,5;{self.available_date_5}:1,2,3,4,5;'
        }  # 預約25個時段，合計 750 分鐘
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))
        print(f"750:response.content  {str(response.content, 'utf8')}")

        self.assertEqual(
            (
                0,
                20,
                0,
                90,
                1160,
                640
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=1).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=1).first().withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=2).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=2).first().withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=3).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=3).first().withholding_minutes,
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values())
            # 測試預扣時數與可動用時數是否正確
        
        self.assertEqual(
            (
                1,
                f'{self.available_date_1}:1,2,3,4,5;{self.available_date_2}:1,2,3,4,5;{self.available_date_3}:1,2,3,4,5;{self.available_date_4}:1,2,3,4,5;{self.available_date_5}:1,2,3,4,5;',
                1160
            ),
            (
                lesson_booking_info.objects.count(),
                lesson_booking_info.objects.first().booking_date_and_time,
                lesson_booking_info.objects.first().remaining_minutes
            )
        )

    
    def test_if_api_changing_lesson_booking_status_exist(self):
        
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 600
        ).save()  # 建立一個 10:90 set

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:1,2,3,4,5;{self.available_date_3}:1,2,3,5;'
        }  # 預約9個時段，合計270分鐘
        self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=booking_post_data)
        
        changing_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.first().id,
            'bookingStatus': 'canceled'
        }

        response = self.client.post(path='/api/lesson/changingBookingStatus', data=changing_post_data)

        self.assertEqual(response.status_code, 200, str(response.content, "utf8"))
        



        

        

        





        



