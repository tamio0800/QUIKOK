from lesson.views import booking_lessons
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
from account.models import general_available_time, student_profile, teacher_profile
from account.models import specific_available_time
from django.contrib.auth.models import Permission, User, Group
from unittest import skip
from lesson.models import lesson_booking_info
from account_finance.models import student_purchase_record, student_remaining_minutes_of_each_purchased_lesson_set


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

        # print(f"for_browsing str(response.content, 'utf8')  {str(response.content, 'utf8')}")
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
        }  # 建立學生1號
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name2 = 'test_student2@a.com'
        student_post_data2 = {
            'regEmail': self.test_student_name2,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }  # 建立學生2號
        self.client.post(path='/api/account/signupStudent/', data=student_post_data2)
        
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
            available_remaining_minutes = 30
        ).save()  # 建立一個試教 set
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.count(), 1,
        student_remaining_minutes_of_each_purchased_lesson_set.objects.values())
        #print(f'student_remaining_minutes_of_each_purchased_lesson_set.objects.values(), \
        #{student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:2;'
        }  # 只預約 30min >> ok

        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)

        self.assertIn('success', str(response.content, 'utf8'))
        
        the_available_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first()
        the_available_remaining_minutes_object.available_remaining_minutes = 30
        the_available_remaining_minutes_object.save()  # 重建 30 分鐘的額度

        self.assertEqual(
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().available_remaining_minutes,
            30,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )

        booking_post_data['bookingDateTime'] = f'{self.available_date_2}:4;'
        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  
        # 只預約 30min >> ok

        the_available_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first()
        the_available_remaining_minutes_object.available_remaining_minutes = 30
        the_available_remaining_minutes_object.save()  # 重建 30 分鐘的額度

        self.assertIn('success', str(response.content, 'utf8'))

        booking_post_data['bookingDateTime'] = f'{self.available_date_1}:3;{self.available_date_2}:4;'
        # print(f"booking_post_data['bookingDateTime'] {booking_post_data['bookingDateTime']}")
        # 預約了1小時，超過 30min 的額度 >> rejected

        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  

        self.assertIn('failed', str(response.content, 'utf8'))
        #print(f'response.content:  {str(response.content, "utf8")}')

        booking_post_data['bookingDateTime'] = ''
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  
        # 沒有回傳時段，應該會是錯誤
        self.assertIn('failed', str(response.content, 'utf8'))

        booking_post_data['bookingDateTime'] = f'{self.available_date_1}:;{self.available_date_2}:5;'
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  
        self.assertIn('success', str(response.content, 'utf8'))

        the_available_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first()
        the_available_remaining_minutes_object.available_remaining_minutes = 150
        the_available_remaining_minutes_object.save()  # 重建 150 分鐘的額度

        booking_post_data['bookingDateTime'] = f'{self.available_date_1}:;{self.available_date_2}:1,2,3,4,5;'
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  
        self.assertIn('failed', str(response.content, 'utf8'))
        # 因為是試教，最多只能預約1堂課(30min)


    def test_if_booking_trial_lessons_split_each_continuous_times_to_bookings(self):
        '''
        這個函式在測試  假設學生預約 2020-01-01:1,2,3,5,6,7;，應該分成2筆預約：
            2020-01-01:1,2,3;
            2020-01-01:5,6,7;
        如果是2020-01-01:1,2,3,5,6,7;2020-01-02:6,7,8;，則應該是3筆預約：
            2020-01-01:1,2,3;
            2020-01-01:5,6,7;
            2020-01-02:6,7,8;
        '''
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
            'bookingDateTime': f'{self.available_date_1}:1,2,4,5,6;'
        }  # 應該拆成兩筆 預約訂單
        self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertEqual(
            lesson_booking_info.objects.filter(student_auth_id=student_profile.objects.first().auth_id).count(),
            2
        )


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
        self.assertEqual(30,
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
            'bookingDateTime': f'{self.available_date_1}:;{self.available_date_3}:1;'
        }  # 預約1堂
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'))
        self.assertEqual(0,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().available_remaining_minutes)
        self.assertEqual(30,
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
                f'{self.available_date_3}:1;',
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
            'bookingDateTime': f'{self.available_date_3}:1;'
        }  # 預約1堂，應該要成功
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'), booking_post_data)
        self.assertEqual(0,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().available_remaining_minutes)
        self.assertEqual(30,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.first().withholding_minutes)
        print(f'student_remaining_minutes_of_each_purchased_lesson_set4  \
            {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')


    def test_if_booking_common_lessons_modified_remaining_minutes_after_booking_successfully(self):
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 30  
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
            'bookingDateTime': f'{self.available_date_1}:3;'
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
                5, 1160
            ),
            (
                lesson_booking_info.objects.count(),
                lesson_booking_info.objects.first().remaining_minutes
            )
        )
        self.assertListEqual(
            [
                f'{self.available_date_1}:1,2,3,4,5;', f'{self.available_date_2}:1,2,3,4,5;',
                f'{self.available_date_3}:1,2,3,4,5;', f'{self.available_date_4}:1,2,3,4,5;',
                f'{self.available_date_5}:1,2,3,4,5;'
            ],
            list(lesson_booking_info.objects.values_list('booking_date_and_time', flat=True))
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
        }  # 預約9個時段，合計270分鐘  > 分成 3 個預約
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertEqual(lesson_booking_info.objects.count(), 3)
        
        changing_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.first().id,
            'bookingStatus': 'canceled'
        }
        response = self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)

        self.assertEqual(response.status_code, 200, str(response.content, "utf8"))


    def test_if_api_changing_lesson_booking_status_to_confirmed(self):
        # 這個是測試可以把預約狀態改成確認，理論上不需要做其他事，相對簡單
        # 記得要到 lesson_sales_sets 的預約成功 +1
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
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        changing_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.first().id,
            'bookingStatus': 'confirmed'
        }
        response = self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)

        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertEqual('confirmed', lesson_booking_info.objects.filter(id=lesson_booking_info.objects.first().id).first().booking_status)
        self.assertEqual('student', lesson_booking_info.objects.filter(id=lesson_booking_info.objects.first().id).first().last_changed_by)


    def test_if_api_changing_lesson_booking_status_to_canceled_trial_lesson(self):
        # 這個是測試可以把試教的預約狀態改成取消
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 30
        ).save()  # 建立一個 trial set
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_3}:5;'
        }  # 預約1個時段，合計30分鐘
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)

        changing_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.first().id,
            'bookingStatus': 'canceled'
        } # 這次測試一下老師發起的取消
        response = self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertEqual('canceled', lesson_booking_info.objects.filter(id=lesson_booking_info.objects.first().id).first().booking_status)
        self.assertEqual('teacher', lesson_booking_info.objects.filter(id=lesson_booking_info.objects.first().id).first().last_changed_by)
        self.assertEqual(
            (
                30, 0
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_id=1,
                    lesson_set_id=lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_id=1,
                    lesson_set_id=lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id
                ).first().withholding_minutes
            )
        )  # 測試時數有真的改回去

    
    def test_if_api_changing_lesson_booking_status_to_canceled_single_set_common_lesson(self):
        # 這個是測試可以把一般的課程預約狀態改成取消(只從單一方案扣時數)
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
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        changing_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.first().id,
            'bookingStatus': 'canceled'
        } # 這次測試一下老師發起的取消
        response = self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)

        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertEqual('canceled', lesson_booking_info.objects.filter(id=lesson_booking_info.objects.first().id).first().booking_status)
        self.assertEqual('teacher', lesson_booking_info.objects.filter(id=lesson_booking_info.objects.first().id).first().last_changed_by)
        
        canceled_minutes = \
            len(lesson_booking_info.objects.first().booking_date_and_time.split(':')[1].split(',')) * 30
        self.assertEqual(
            (
                330 + canceled_minutes, 270 - canceled_minutes
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_id=1,
                    lesson_set_id=lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_id=1,
                    lesson_set_id=lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id
                ).first().withholding_minutes
            )
        )  # 測試時數有真的改回去

    
    def test_if_api_changing_lesson_booking_status_to_canceled_multiple_sets_common_lesson(self):
        # 這個是測試可以把一般的課程預約狀態改成取消(只從單一方案扣時數)
        student_remaining_1 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 20)  
        student_remaining_1.save()  # 建立一個 10:90 set  20min
        student_remaining_2 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 60)  
        student_remaining_2.save()  # 建立一個 10:90 set  60min
        student_remaining_3 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 260)  
        student_remaining_3.save()  # 建立一個 10:90 set  260min

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:1,2,3,4,5;{self.available_date_3}:1,2,3,5;{self.available_date_1}:3,5;'
        }  # 預約9個時段，合計330分鐘  >>  5 bookings
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertEqual(
            (
                10, 250, 0, 60, 0, 20
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_3.id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_3.id
                ).first().withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_2.id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_2.id
                ).first().withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_1.id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_1.id
                ).first().withholding_minutes
            )
        )  # 測試一下是否真的有預扣時數成功

        for each_booking_id in list(lesson_booking_info.objects.values_list('id', flat=True)):
            changing_post_data = {
                'userID': student_profile.objects.first().auth_id,
                'bookingID': each_booking_id,
                'bookingStatus': 'canceled'
            } # 測試一下學生發起的取消
            response = self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertEqual('canceled', lesson_booking_info.objects.filter(id=lesson_booking_info.objects.first().id).first().booking_status)
        self.assertEqual('student', lesson_booking_info.objects.filter(id=lesson_booking_info.objects.first().id).first().last_changed_by)
        self.assertEqual(
            (
                260, 0, 60, 0, 20, 0
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_3.id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_3.id
                ).first().withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_2.id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_2.id
                ).first().withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_1.id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    id=student_remaining_1.id
                ).first().withholding_minutes
            )
        )  # 測試時數有真的改回去

        
    def test_if_api_changing_lesson_booking_status_to_update_teacher_s_specific_time(self):
        student_remaining_1 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 600)  
        student_remaining_1.save()  # 建立一個 10:90 set  600min

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:1,2,3,4,5;{self.available_date_3}:1,2,3,5;{self.available_date_1}:3,5;'
        }  # 預約11個時段，合計330分鐘

        self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)

        self.assertEqual(0, specific_available_time.objects.filter(
            teacher_model=teacher_profile.objects.first(),
            is_occupied=True).count(),
            specific_available_time.objects.values())
        # 目前老師應該沒有被預約的時段

        for each_booking_id in lesson_booking_info.objects.values_list('id', flat=True):
            changing_post_data = {
                'userID': teacher_profile.objects.first().auth_id,
                'bookingID': each_booking_id,
                'bookingStatus': 'confirmed'
            }  # 由老師確認
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        
        self.assertEqual(
            5, 
            specific_available_time.objects.filter(
                teacher_model=teacher_profile.objects.first(),
                is_occupied=True).count(),
            specific_available_time.objects.values().filter(is_occupied=True))
        # 現在應該有五個被預約的時段了  1,2,3,4,5  1,2,3  5  3  5

        self.assertEqual(
            (
                1, 1, 2, 1
            ),
            (
                specific_available_time.objects.filter(
                    teacher_model=teacher_profile.objects.first(),
                    is_occupied=True,
                    time='1,2,3,4,5'
                ).count(),
                specific_available_time.objects.filter(
                    teacher_model=teacher_profile.objects.first(),
                    is_occupied=True,
                    time='1,2,3'
                ).count(),
                specific_available_time.objects.filter(
                    teacher_model=teacher_profile.objects.first(),
                    is_occupied=True,
                    time='5'
                ).count(),
                specific_available_time.objects.filter(
                    teacher_model=teacher_profile.objects.first(),
                    is_occupied=True,
                    time='3'
                ).count()
            ),
            specific_available_time.objects.values().filter(is_occupied=True)
        )  # 確認預約細項無誤
        print(f'specific_available_time.objects.values().filter(is_occupied=True)  \
        {specific_available_time.objects.values().filter(is_occupied=True)}')

        booking_id_to_be_canceled = \
            lesson_booking_info.objects.get(
                booking_date_and_time=f"{self.available_date_2}:1,2,3,4,5;"
            ).id
        print(f'booking_id_to_be_canceled  {booking_id_to_be_canceled, lesson_booking_info.objects.values()}')
        # 接下來來取消這個預約
        changing_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'bookingID': booking_id_to_be_canceled,
            'bookingStatus': 'canceled'
        }  # 換學生取消好了
        response = self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        print(f'booking_id_after_canceled  {booking_id_to_be_canceled, lesson_booking_info.objects.values()}')
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))

        self.assertEqual(
            4,
            specific_available_time.objects.filter(
                teacher_model=teacher_profile.objects.first(),
                is_occupied=True).count(),
            specific_available_time.objects.values().filter(is_occupied=True))
        # 取消一筆預約

        canceled_minutes = 150
        # 學生應該也恢復 600 分鐘的可用時數了
        self.assertEqual(
            (270+canceled_minutes, 330-canceled_minutes),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    student_auth_id = student_profile.objects.first().auth_id,
                    teacher_auth_id = teacher_profile.objects.first().auth_id,
                    lesson_id = 1,
                    lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    student_auth_id = student_profile.objects.first().auth_id,
                    teacher_auth_id = teacher_profile.objects.first().auth_id,
                    lesson_id = 1,
                    lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
                ).first().withholding_minutes
            )
        )


    def test_if_2_students_can_book_overlapped_time_to_a_teacher(self):
        # 測試學生們可否預約同一個老師的重複(部分或完全)時段
        student_remaining_1 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.get(id=1).auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 600)  
        student_remaining_1.save()  # 建立一個 10:90 set  600min  by student 1

        student_remaining_2 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_auth_id = student_profile.objects.get(id=2).auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 30)  
        student_remaining_2.save()  # 建立一個 10:90 set  30min  by student 2

        booking_post_data_1 = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生1 的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:1,2,3,4,5;{self.available_date_3}:1,2,3,5;{self.available_date_1}:3,5;'
        }  # 預約11個時段，合計330分鐘 >> 12345 123 5 3 5  >> 5門課
        response1 = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data_1)

        # 接下來讓學生2 同樣預約 self.available_date_2 的 時段 2
        booking_post_data_2 = {
            'userID': student_profile.objects.get(id=2).auth_id,  # 學生1 的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:2;'
        }  # 預約1個時段，合計30分鐘 >> 1門試教課
        response2 = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data_2)

        self.assertEqual(
            (True, True),
            (
                'success' in str(response1.content, 'utf8'),
                'success' in str(response2.content, 'utf8')
            ),
            str(response2.content, 'utf8')
        )



    def test_get_student_s_available_remaining_minutes_exist(self):
        '''
        測試 取得學生目前對於 某門課程的所有可預約時數 的函式存在
        '''
        post_data = {
            'userID': student_profile.objects.first().id,
            'lessonID': lesson_info.objects.first().id}

        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        
        self.assertEqual(response.status_code, 200)
        
    
    def test_get_student_s_available_remaining_minutes_works_when_having_trial(self):
        '''
        測試 可以取得學生的 可預約時數 及 是否有試教課程還沒用，
        當他有試教課程還沒使用時，是否可以成功回傳其他情況下的正確數值。
        '''
        # 還要建立課程才能測試
        purchase_post_data = \
            {
                'userID':student_profile.objects.first().auth_id,
                'teacherID':teacher_profile.objects.first().auth_id,
                'lessonID':lesson_info.objects.first().id,
                'sales_set': 'trial',
                'total_amount_of_the_sales_set': 69,
                'q_discount':0}

        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 建立購買資料
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))

        post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.first().id}
        # 先嘗試查詢看看
        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        # 因為還未確認付款成功，此時學生應該還沒有可用時數
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 0', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": false', str(response.content, "utf8"), str(response.content, "utf8"))

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生應該有30min的可用時數

        # 確認 資料庫裡面 有正確的資料了
        self.assertEqual(
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                id=1).available_remaining_minutes,
            30
        )
        #print(f'lesson_sales_sets: \
        #    {lesson_sales_sets.objects.values()}')
        #print(f'student_remaining_minutes_of_each_purchased_lesson_set.objects: \
        #    {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')

        post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.first().id}

        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        #self.assertIn('[30, true]', str(response.content, "utf8"),
        #student_remaining_minutes_of_each_purchased_lesson_set.objects.values())
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 30', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": true', str(response.content, "utf8"), str(response.content, "utf8"))
        # 理論上會回傳類似這樣的形式 >> (remaining_minutes(INT), has_unused_trial(Bool))

        # 此時再購買一個 20:80 的方案
        purchase_post_data = \
            {
                'userID':student_profile.objects.first().auth_id,
                'teacherID':teacher_profile.objects.first().auth_id,
                'lessonID':lesson_info.objects.first().id,
                'sales_set': '20:80',
                'total_amount_of_the_sales_set': int(800*20*0.8),
                'q_discount':0}

        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 建立購買資料

        # 再嘗試查詢看看
        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        # 因為還未確認付款成功，此時學生應該只有試教課程，跟可預約的30min
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        #self.assertIn('[30, true]', str(response.content, "utf8"))
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 30', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": true', str(response.content, "utf8"), str(response.content, "utf8"))

        # 如果付款成功...
        the_purchase_object = \
            student_purchase_record.objects.order_by('-update_time').first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()

        # 再一次嘗試查詢看看
        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        # 因為確認付款成功，此時學生應該有試教課程，跟可預約的30min + 1200min = 1230min
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        #self.assertIn('[1230, true]', str(response.content, "utf8"))
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 1230', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": true', str(response.content, "utf8"), str(response.content, "utf8"))


    def test_get_student_s_available_remaining_minutes_works_when_not_having_trial(self):
        '''
        測試 可以取得學生的 可預約時數 及 是否有試教課程還沒用，
        當他沒有試教課程還沒使用時，是否可以成功回傳其他情況下的正確數值。
        '''
        # 此時再購買一個 20:80 的方案
        purchase_post_data = \
            {
                'userID':student_profile.objects.first().auth_id,
                'teacherID':teacher_profile.objects.first().auth_id,
                'lessonID':lesson_info.objects.first().id,
                'sales_set': '30:75',
                'total_amount_of_the_sales_set': int(800*30*0.75),
                'q_discount':0}

        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 建立購買資料

        post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.first().id}

        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        # 因為還沒確認付款，故應該會失敗
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 0', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": false', str(response.content, "utf8"), str(response.content, "utf8"))

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生應該有1800min的可用時數

        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)

        #self.assertIn('[1800, false]', str(response.content, "utf8"),
        #student_remaining_minutes_of_each_purchased_lesson_set.objects.values())
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 1800', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": false', str(response.content, "utf8"), str(response.content, "utf8"))

    
    def test_get_student_s_available_remaining_minutes_works_after_booking_trial_successfully(self):
        '''
        測試學生預約試教後，回傳資訊正不正確
        '''
        purchase_post_data = \
            {
                'userID':student_profile.objects.first().auth_id,
                'teacherID':teacher_profile.objects.first().auth_id,
                'lessonID':lesson_info.objects.first().id,
                'sales_set': 'trial',
                'total_amount_of_the_sales_set': 69,
                'q_discount':0}

        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 建立購買資料
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生應該有30min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:2;'
        }  # 只預約 30min >> ok

        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約

        post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.first().id}

        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        # 此時因為已經預約的關係，學生應該會呈現沒有可用的 試教 與可用時數
        #self.assertIn('[0, false]', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 0', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": false', str(response.content, "utf8"), str(response.content, "utf8"))

    
    def test_get_student_s_available_remaining_minutes_works_after_booking_common_successfully(self):
        '''
        測試學生預約一般課程後，回傳資訊正不正確
        '''
        purchase_post_data = \
            {
                'userID':student_profile.objects.first().auth_id,
                'teacherID':teacher_profile.objects.first().auth_id,
                'lessonID':lesson_info.objects.first().id,
                'sales_set': '10:90',
                'total_amount_of_the_sales_set': int(800*10*0.9),
                'q_discount':0}

        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 建立購買資料
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生應該有600min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:1,2,5;{self.available_date_2}:1,2,3,4,5;{self.available_date_4}:1,3,4;'
        }  # 預約 330min

        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約

        post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.first().id}

        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        # 此時因為已經預約的關係，學生應該會呈現沒有可用的 試教 與 270min可用時數
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 270', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": false', str(response.content, "utf8"), str(response.content, "utf8"))


class TEACHER_BOOKING_HISTORY_TESTS(TestCase):
    
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
            shutil.rmtree('user_upload/students/' + self.test_student_name1)
            shutil.rmtree('user_upload/students/' + self.test_student_name2)
            shutil.rmtree('user_upload/students/' + self.test_student_name3)
            shutil.rmtree('user_upload/teachers/' + self.test_username)
        except:
            pass

    
    def test_get_teacher_s_booking_history_api_exist(self):
        '''
        測試 回傳該名老師所有預約、課程的狀態 這支api 存在
        {
            userID (teacher_auth_id)
            filtered_by: string // 依照什麼做篩選 _狀態
                    字串顯示：
                            /預約成功（confirmed）
                            /待回覆（to_be_confirmed）
                            /已完課（finished）
                            /已取消（canceled）
            registered_from_date//起始日期1990-01-01
            registered_to_date//結束日期1990-01-01
        }
        ''' 
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2000-01-01',
            'registered_to_date': '2021-01-31'
        }

        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        
        self.assertEqual(response.status_code, 200, str(response.content, "utf8"))

    
    def test_get_teacher_s_booking_history_api_work_when_teacher_has_no_booking_history_at_all(self):
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': '',
            'registered_from_date': '2000-01-01',
            'registered_to_date': '2050-01-31'
        }

        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"data": null', str(response.content, "utf8"))

    
    def test_get_teacher_s_booking_history_api_work_when_teacher_auth_id_not_exist(self):
        booking_history_post_data = {
            'userID': 35,
            'filtered_by': '',
            'registered_from_date': '2000-01-01',
            'registered_to_date': '2021-01-31'
        }

        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        
        self.assertIn('failed', str(response.content, "utf8"))

     
    def test_get_teacher_s_booking_history_work_when_teacher_has_common_lessons_filtered_and_not(self):
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有600min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:1,2,5;{self.available_date_2}:1,2,3,4,5;{self.available_date_4}:1,3,4;'
        }  # 預約 330min  >> 5門課

        self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師應該有5則 待確認 預約訊息
        
        self.assertEquals(5, 
        lesson_booking_info.objects.filter(teacher_auth_id=teacher_profile.objects.first().auth_id).count(),
        lesson_booking_info.objects.values())
        
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件

        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        
        print(f'has_common_lessons_to_be_confirmed_1 {str(response.content, "utf8")}')
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_1}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_2}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_4}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_status": "to_be_confirmed"', str(response.content, "utf8"))

        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': '',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        } # 無篩選條件
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_1}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_2}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_4}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_status": "to_be_confirmed"', str(response.content, "utf8"))

        # 接下來取消兩門課，第二門跟第三門
        for booking_id_to_be_canceled in [lesson_booking_info.objects.all()[1].id, lesson_booking_info.objects.all()[2].id]:
            changing_post_data = {
                'userID': student_profile.objects.first().auth_id,
                'bookingID': booking_id_to_be_canceled,
                'bookingStatus': 'canceled'
            }  # 換學生取消
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件篩 to_be_confirmed
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(3, str(response.content, "utf8").count('to_be_confirmed'),
        str(response.content, "utf8")) # 應該只有3門 to_be_confirmed
        self.assertEquals(3, str(response.content, "utf8").count('remaining_time'),
        str(response.content, "utf8")) # 並且總共只有3筆資料

        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': 'canceled',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件篩 to_be_confirmed
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(0, str(response.content, "utf8").count('to_be_confirmed'),
        str(response.content, "utf8")) # 應該只有0門 to_be_confirmed
        self.assertEquals(2, str(response.content, "utf8").count('canceled'),
        str(response.content, "utf8")) # 並且總共只有2筆 canceled

        changing_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.first().id,
            'bookingStatus': 'confirmed'
        }  # 接下來老師確認第一筆的預約
        self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': 'confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件篩 confirmed
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"confirmed"'),
        str(response.content, "utf8")) # 應該只有1門 confirmed
        self.assertEquals(1, str(response.content, "utf8").count('remaining_time'),
        str(response.content, "utf8")) # 並且總共只有1筆資料

        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2011-01-01'
        }  # 測試沒篩選條件篩  選擇古老的日期
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(0, str(response.content, "utf8").count('"confirmed"'),
        str(response.content, "utf8")) # 應該只有0門 confirmed
        self.assertEquals(0, str(response.content, "utf8").count('remaining_time'),
        str(response.content, "utf8")) # 並且總共只有0筆資料

        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試沒篩選條件篩  >> 這時應該有 confirmed_1, canceled_2, to_be_confirmed_2, 
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"confirmed"'),
        str(response.content, "utf8")) # 應該只有1門 confirmed
        self.assertEquals(2, str(response.content, "utf8").count('"canceled"'),
        str(response.content, "utf8")) # 應該只有2門 canceled
        self.assertEquals(2, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該只有2門 to_be_confirmed
        self.assertEquals(5, str(response.content, "utf8").count('remaining_time'),
        str(response.content, "utf8")) # 並且總共有5筆資料

        # 此時帶入學生2號
        purchase_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        the_purchase_object = \
            student_purchase_record.objects.get(student_auth_id=student_profile.objects.get(id=2).auth_id)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有600min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:1,2,3,4,5;{self.available_date_4}:1,2,3,4;'
        }  # 預約 270min  >> 2門課
        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師 會再加上 2 則待確認預約訊息，總共 >>
            # confirmed_1, canceled_2, to_be_confirmed_4
        
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01'
        } 
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(4, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該有4門 to_be_confirmed

        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01'
        } 
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(7, str(response.content, "utf8").count('"remaining_time"'),
        str(response.content, "utf8")) # 共7筆預約 

        
    def test_get_teacher_s_booking_history_work_when_teacher_has_trial_and_no_discount_lessons_filtered_and_not(self):
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有30min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:4;'
        }  # 預約 30min  >> 1門課

        self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師應該有1則 待確認 預約訊息

        self.assertEquals(1, 
        lesson_booking_info.objects.filter(teacher_auth_id=teacher_profile.objects.first().auth_id).count(),
        lesson_booking_info.objects.values())
        
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_2}"', str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該只有1門 to_be_confirmed
        self.assertEquals(1, str(response.content, "utf8").count('"booked_time"'),
        str(response.content, "utf8")) # 共1筆
        self.assertIn(f'"discount_price": "trial"', str(response.content, "utf8"))
        

        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': 'no_discount',
            'total_amount_of_the_sales_set': 800,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        
        the_purchase_object = \
            student_purchase_record.objects.get(id=2)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有60min的可用時數
        print(f'student_remaining_minutes_of_each_purchased_lesson_set.XX {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        self.assertEquals(
            60,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(lesson_set_id=2).available_remaining_minutes,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values())

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_3}:4;{self.available_date_1}:1;'
        }  # 預約 60min  >> 2門課

        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師應該總共有3則 待確認 預約訊息
        self.assertIn('success', str(response.content, 'utf8'))

        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(3, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該有3門 to_be_confirmed
        self.assertEquals(3, str(response.content, "utf8").count('"booked_time"'),
        str(response.content, "utf8")) # 共3筆
        self.assertEquals(2, str(response.content, "utf8").count('"discount_price": "no_discount"'),
        str(response.content, "utf8")) # 共2筆
        self.assertEquals(1, str(response.content, "utf8").count('"discount_price": "trial"'),
        str(response.content, "utf8")) # 共1筆

        # 加入學生 auth_id = 2
        purchase_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        the_purchase_object = \
            student_purchase_record.objects.get(id=3)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生2應該有600min的可用時數
        print(f'student_remaining_minutes_of_each_purchased_lesson_set.XX {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        self.assertEquals(
            600,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                student_auth_id=student_profile.objects.get(id=2).auth_id).available_remaining_minutes,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values())

        booking_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_3}:4,5;{self.available_date_1}:1,2,3,5;'
        }  # 預約 180min  >> 3門課

        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師應該總共有6則 待確認 預約訊息
        self.assertIn('success', str(response.content, 'utf8'))

        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'filtered_by': '',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試無篩選條件
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(6, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該有6門 to_be_confirmed
        self.assertEquals(6, str(response.content, "utf8").count('"booked_time"'),
        str(response.content, "utf8")) # 共6筆
        self.assertEquals(3, str(response.content, "utf8").count('"discount_price": "10:90"'),
        str(response.content, "utf8")) # 共3筆
        self.assertEquals(3, str(response.content, "utf8").count('"remaining_time": 0'),
        str(response.content, "utf8")) # 共3筆
        self.assertEquals(3, str(response.content, "utf8").count('"remaining_time": 420'),
        str(response.content, "utf8")) # 共3筆


class STUDENT_BOOKING_HISTORY_TESTS(TestCase):
    
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
        teacher_post_data = {
            'regEmail': self.test_teacher_name2,
            'regPwd': '00000000',
            'regName': 'test_name',
            'regNickname': 'test_nickname',
            'regBirth': '2000-01-01',
            'regGender': '0',
            'intro': 'test_intro',
            'regMobile': '0912-345678',
            'tutor_experience': '十年以上',
            'subject_type': 'test_subject',
            'education_1': 'education_1_test',
            'education_2': 'education_2_test',
            'education_3': 'education_3_test',
            'company': 'test_company',
            'special_exp': 'test_special_exp',
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:1,2,3,4,5;4:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        
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
        
        # 建立課程
        lesson_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,   # 這是老師的auth_id
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

        lesson_post_data = {
            'userID': teacher_profile.objects.get(id=2).auth_id,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 1200,
            'discount_price': '5:90;20:80;30:70;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': -999,
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
        self.available_date_1_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1)).first().date
        self.available_date_2_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1))[1].date
        self.available_date_3_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1))[2].date
        self.available_date_4_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1))[3].date
        self.available_date_5_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1))[4].date

        self.available_date_1_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2)).first().date
        self.available_date_2_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[1].date
        self.available_date_3_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[2].date
        self.available_date_4_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[3].date
        self.available_date_5_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[4].date


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name1)
            shutil.rmtree('user_upload/students/' + self.test_student_name2)
            shutil.rmtree('user_upload/students/' + self.test_student_name3)
            shutil.rmtree('user_upload/teachers/' + self.test_username)
        except:
            pass


