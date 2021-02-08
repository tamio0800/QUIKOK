from handy_functions import turn_first_datetime_string_into_time_format
from lesson.views import booking_lessons
from django.test import TestCase, Client
from django.core import mail
import os
import shutil
from lesson.models import (lesson_completed_record, lesson_info_for_users_not_signed_up, 
                            lesson_info, lesson_card, lesson_sales_sets)
from account.models import (general_available_time, student_profile, teacher_profile,
                            specific_available_time)
from django.contrib.auth.models import Permission, User, Group
from unittest import skip
from lesson.models import lesson_booking_info
from account_finance.models import student_purchase_record, student_remaining_minutes_of_each_purchased_lesson_set
from datetime import datetime, timedelta, date as date_function
from account_finance.models import student_owing_teacher_time
from lesson.models import lesson_reviews_from_students, student_reviews_from_teachers
from account.models import student_review_aggregated_info, teacher_review_aggregated_info
from django.core import mail
# 10.344
# python3 manage.py test lesson/ --settings=Quikok.settings_for_test
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
            sorted(['trial', 'no_discount', '10:90', '20:80', '30:75']),
            sorted(all_lesson_1_sales_sets),
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
            sorted(['5:95', '10:90', '50:70']),
            sorted(list(lesson_sales_sets.objects.values_list('sales_set', flat=True).filter(is_open=True)))
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
            'lessonID': lesson_info.objects.get(id=1).id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
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
        # 確認是否有產生datetime形式的預約起始時間點
        self.assertEqual(
            turn_first_datetime_string_into_time_format(f'{self.available_date_1}:2;'),
            lesson_booking_info.objects.get(id=1).booking_start_datetime,
            lesson_booking_info.objects.get(id=1).booking_start_datetime)

        #self.fail(
        #    (turn_first_datetime_string_into_time_format(f'{self.available_date_1}:2;'),
        #    lesson_booking_info.objects.get(id=1).booking_start_datetime))
        
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
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


    def test_when_student_booking_lessons_send_email_to_teacher(self):
        '''當學生發出預約的時候，系統要寄email提醒老師確認時間。
        檢查系統是否有發出這封信'''
        mail.outbox = [] # 清空暫存記憶裡的信
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 60  
        ).save()  # 建立一個訂單
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1}:3;'
        }  
        response = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, 'utf8'))
        # 檢查是否有寄出提醒信
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Quikok!開課通知：有學生預約上課！')
    

    def test_if_booking_trial_lessons_modified_remaining_minutes_after_booking_successfully(self):
        '''
        這個測試用在檢查：當試教預約成功後，是否有從學生那邊扣除剩餘時數，並進行對應的資料庫更新。
        '''
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
            available_remaining_minutes = 30  
        ).save()  # 先建立一個試教 set
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
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
                    lesson_sales_set_id=lesson_sales_sets.objects.filter(
                        teacher_auth_id=teacher_profile.objects.first().auth_id,
                        sales_set='10:90'
                    ).first().id
                ).first().withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_sales_set_id=lesson_sales_sets.objects.filter(
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 20)
        student_remaining_minutes_1.save()  # 建立一個 10:90 set，只有 20 分鐘
        student_remaining_minutes_2 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 90)
        student_remaining_minutes_2.save()  # 建立一個 10:90 set，只有 90 分鐘  # 再建立一個 10:90 set，只有 90 分鐘
        student_remaining_minutes_3 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='30:75').filter(is_open=True).first().id,
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
            sorted([
                f'{self.available_date_1}:1,2,3,4,5;', f'{self.available_date_2}:1,2,3,4,5;',
                f'{self.available_date_3}:1,2,3,4,5;', f'{self.available_date_4}:1,2,3,4,5;',
                f'{self.available_date_5}:1,2,3,4,5;'
            ]),
            sorted(list(lesson_booking_info.objects.values_list('booking_date_and_time', flat=True)))
        )

    
    def test_if_api_changing_lesson_booking_status_exist(self):
        
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id,
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
                    lesson_sales_set_id=lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_id=1,
                    lesson_sales_set_id=lesson_sales_sets.objects.filter(sales_set='trial').filter(is_open=True).first().id
                ).first().withholding_minutes
            )
        )  # 測試時數有真的改回去

    
    def test_if_api_changing_lesson_booking_status_to_canceled_single_set_common_lesson(self):
        # 這個是測試可以把一般的課程預約狀態改成取消(只從單一方案扣時數)
        student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
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
                    lesson_sales_set_id=lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    lesson_id=1,
                    lesson_sales_set_id=lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id
                ).first().withholding_minutes
            )
        )  # 測試時數有真的改回去

    
    def test_if_api_changing_lesson_booking_status_to_canceled_multiple_sets_common_lesson(self):
        # 這個是測試可以把一般的課程預約狀態改成取消(只從單一方案扣時數)
        student_remaining_1 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 20)  
        student_remaining_1.save()  # 建立一個 10:90 set  20min
        student_remaining_2 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
            available_remaining_minutes = 60)  
        student_remaining_2.save()  # 建立一個 10:90 set  60min
        student_remaining_3 = student_remaining_minutes_of_each_purchased_lesson_set.objects.create(
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
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
            student_purchase_record_id = 1,
            student_auth_id = student_profile.objects.first().auth_id,
            teacher_auth_id = teacher_profile.objects.first().auth_id,
            lesson_id = 1,
            lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
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
                    student_purchase_record_id = 1,
                    student_auth_id = student_profile.objects.first().auth_id,
                    teacher_auth_id = teacher_profile.objects.first().auth_id,
                    lesson_id = 1,
                    lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
                ).first().available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                    student_purchase_record_id = 1,
                    student_auth_id = student_profile.objects.first().auth_id,
                    teacher_auth_id = teacher_profile.objects.first().auth_id,
                    lesson_id = 1,
                    lesson_sales_set_id = lesson_sales_sets.objects.filter(sales_set='10:90').filter(is_open=True).first().id,
                ).first().withholding_minutes
            )
        )

    
    def test_if_2_students_can_book_overlapped_time_to_a_teacher(self):
        # 測試學生們可否預約同一個老師的重複(部分或完全)時段
        order_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800 * 10 * 0.9),
            'q_discount':0
        }  #測試 trial 看看是否成功
        self.client.post(path='/api/account_finance/storageOrder/', data=order_post_data)
        # 將它設定為已付款

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_student_purchase_record_object = \
            student_purchase_record.objects.get(student_auth_id=student_profile.objects.get(id=1).auth_id)
        the_student_purchase_record_object.payment_status = 'paid'
        the_student_purchase_record_object.save()  # 學生1號設定完成

        order_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'teacherID': teacher_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0
        }  #測試 trial 看看是否成功
        response = self.client.post(path='/api/account_finance/storageOrder/', data=order_post_data)
        # 將它設定為已付款
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))
        
        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        
        the_student_purchase_record_object = \
            student_purchase_record.objects.get(student_auth_id=student_profile.objects.get(id=2).auth_id)
        the_student_purchase_record_object.payment_status = 'paid'
        the_student_purchase_record_object.save()  # 學生2號設定完成
        self.assertEqual(30, 
        student_remaining_minutes_of_each_purchased_lesson_set.objects.get(student_auth_id=student_profile.objects.get(id=2).auth_id).available_remaining_minutes,
        student_remaining_minutes_of_each_purchased_lesson_set.objects.values().filter(student_auth_id=student_profile.objects.get(id=2).auth_id))

        booking_post_data_1 = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生1 的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2}:1,2,3,4,5;{self.available_date_3}:1,2,3,5;{self.available_date_1}:3,5;'
        }  # 預約11個時段，合計330分鐘 >> 12345 123 5 3 5  >> 5門課
        response1 = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data_1)
        self.assertEqual(5, 
            lesson_booking_info.objects.filter(student_auth_id=student_profile.objects.get(id=1).auth_id).count(),
            lesson_booking_info.objects.values().filter(student_auth_id=student_profile.objects.get(id=1).auth_id))
        self.assertEqual(600-330,
            lesson_booking_info.objects.filter(student_auth_id=student_profile.objects.get(id=1).auth_id).first().remaining_minutes,
            lesson_booking_info.objects.values().filter(student_auth_id=student_profile.objects.get(id=1).auth_id))

        self.assertEqual(
                (600-330, 330),
                (
                    student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                        student_auth_id=student_profile.objects.get(id=1).auth_id).available_remaining_minutes,
                    student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                        student_auth_id=student_profile.objects.get(id=1).auth_id).withholding_minutes
                ),
                lesson_booking_info.objects.values().filter(student_auth_id=student_profile.objects.get(id=1).auth_id)
            )  # 測試是否如預期般被扣除

        # 接下來讓學生2 同樣預約 self.available_date_2 的 時段 2
        booking_post_data_2 = {
            'userID': student_profile.objects.get(id=2).auth_id,  # 學生2 的auth_id
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
        ) # 測試能不能同時兩個學生預約重疊的時間

        changing_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.get(
                student_auth_id=student_profile.objects.get(id=2).auth_id,
                booking_date_and_time=f'{self.available_date_2}:2;'
            ).id,
            'bookingStatus': 'confirmed'
        } # 接下來測試看看如果老師接受了學生2的試教，會不會取消學生1的對應的預約
        response = self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))

        self.assertEqual(
            'canceled',
            lesson_booking_info.objects.get(
                student_auth_id=student_profile.objects.get(id=1).auth_id,
                booking_date_and_time=f'{self.available_date_2}:1,2,3,4,5;'
            ).booking_status,
            lesson_booking_info.objects.values().filter(
                student_auth_id=student_profile.objects.get(id=1).auth_id,
                booking_date_and_time=f'{self.available_date_2}:1,2,3,4,5;'
            ).first()
        )  # 如果老師接受了學生2的試教，應該取消學生1的對應的預約

        # 讓學生2再預約一點課程
        order_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'teacherID': teacher_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '20:80',
            'total_amount_of_the_sales_set': int(20*800*0.8),
            'q_discount':0
        }  #測試 trial 看看是否成功
        response = self.client.post(path='/api/account_finance/storageOrder/', data=order_post_data)
        # 將它設定為已付款
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))
        
        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = 1,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '20:80',
                    lesson_id = 1
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        
        the_student_purchase_record_object = \
            student_purchase_record.objects.filter(
                student_auth_id=student_profile.objects.get(id=2).auth_id,
                price=int(20*800*0.8),
                ).first()
        the_student_purchase_record_object.payment_status = 'paid'
        the_student_purchase_record_object.save()  # 學生2號設定完成
        self.assertEqual(2,
            student_purchase_record.objects.filter(
                student_auth_id=student_profile.objects.get(id=2).auth_id).count(),
            student_purchase_record.objects.values().filter(
                student_auth_id=student_profile.objects.get(id=2).auth_id))
        #print(f'student_purchase_record.objects.values()XX \
        #    {student_purchase_record.objects.values().filter(student_auth_id=student_profile.objects.get(id=2).auth_id)}')
        #print(student_remaining_minutes_of_each_purchased_lesson_set.objects.values().filter(
        #    student_auth_id=student_profile.objects.get(id=2).auth_id
        #))
        
        booking_post_data_3 = {
            'userID': student_profile.objects.get(id=2).auth_id,  # 學生2 的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_3}:1,2;'
        }  # 預約2個時段，合計60分鐘 >> 12  >> 1門課
        response3 = self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data_3)
        
        self.assertIn('success', str(response3.content, 'utf8'), str(response3.content, 'utf8'))
        self.assertEqual(
            'to_be_confirmed',
            lesson_booking_info.objects.get(
                student_auth_id=student_profile.objects.get(id=2).auth_id,
                booking_date_and_time=f'{self.available_date_3}:1,2;'
            ).booking_status,
            lesson_booking_info.objects.values().filter(
                student_auth_id=student_profile.objects.get(id=2).auth_id,
                booking_date_and_time=f'{self.available_date_3}:1,2;'
            ).first()
        )

        changing_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.get(
                student_auth_id=student_profile.objects.get(id=1).auth_id,
                booking_date_and_time=f'{self.available_date_3}:1,2,3;'
            ).id,
            'bookingStatus': 'confirmed'
        } # 接下來測試看看如果老師接受了學生1的{self.available_date_3}:1,2,3，會不會取消學生2的新建預約
        response = self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))

        self.assertEqual(
            'canceled',
            lesson_booking_info.objects.filter(
                student_auth_id=student_profile.objects.get(id=2).auth_id,
                booking_date_and_time=f'{self.available_date_3}:1,2;'
            ).first().booking_status,
            lesson_booking_info.objects.values().filter(
                student_auth_id=student_profile.objects.get(id=2).auth_id)
        )  # 如果老師接受了學生1{self.available_date_3}:1,2,3，應該取消學生2的對應的預約


    def test_get_student_s_available_remaining_minutes_exist(self):
        '''
        測試 取得學生目前對於 某門課程的所有可預約時數 的函式存在
        '''
        post_data = {
            'userID': student_profile.objects.first().id,
            'lessonID': lesson_info.objects.get(id=1).id}

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
                'lessonID':lesson_info.objects.get(id=1).id,
                'sales_set': 'trial',
                'total_amount_of_the_sales_set': 69,
                'q_discount':0}

        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 建立購買資料
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))

        post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.get(id=1).id}
        # 先嘗試查詢看看
        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        # 因為還未確認付款成功，此時學生應該還沒有可用時數
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 0', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": false', str(response.content, "utf8"), str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

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
            'lessonID': lesson_info.objects.get(id=1).id}

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
                'lessonID':lesson_info.objects.get(id=1).id,
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

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '20:80',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        # 如果付款成功...
        the_purchase_object = \
            student_purchase_record.objects.order_by('-updated_time').first()
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
                'lessonID':lesson_info.objects.get(id=1).id,
                'sales_set': '30:75',
                'total_amount_of_the_sales_set': int(800*30*0.75),
                'q_discount':0}

        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 建立購買資料

        post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lessonID': lesson_info.objects.get(id=1).id}

        response = self.client.post(
            path='/api/lesson/getStudentsAvailableRemainingMinutes/',
            data=post_data)
        # 因為還沒確認付款，故應該會失敗
        self.assertIn('"all_available_remaining_minutes_of_this_lesson": 0', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"student_has_unused_trial_lesson_sales_set": false', str(response.content, "utf8"), str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = 1,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '30:75',
                    lesson_id = 1
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

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
                'lessonID':lesson_info.objects.get(id=1).id,
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
            'lessonID': lesson_info.objects.get(id=1).id}

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
                'lessonID':lesson_info.objects.get(id=1).id,
                'sales_set': '10:90',
                'total_amount_of_the_sales_set': int(800*10*0.9),
                'q_discount':0}

        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 建立購買資料
        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

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
            'lessonID': lesson_info.objects.get(id=1).id}

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
            'regName': 'test_student_name1',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name2 = 'test_student2@a.com'
        student_post_data['regEmail'] = self.test_student_name2
        student_post_data['regName'] = 'test_student_name2'
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name3 = 'test_student3@a.com'
        student_post_data['regEmail'] = self.test_student_name3
        student_post_data['regName'] = 'test_student_name3'
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
            'lesson_title': 'test_lesson_1',
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

        # 建立課程2
        lesson_post_data['lesson_title'] = 'test_lesson_2'
        lesson_post_data['trial_class_price'] = 169
        lesson_post_data['price_per_hour'] = 1300
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
            'searched_by': '',
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
            'searched_by': '',
            'filtered_by': '',
            'registered_from_date': '2000-01-01',
            'registered_to_date': '2050-01-31'
        }

        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', 
            data=booking_history_post_data)
        
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"data": []', str(response.content, "utf8"))

    
    def test_get_teacher_s_booking_history_api_work_when_teacher_auth_id_not_exist(self):
        booking_history_post_data = {
            'userID': 35,
            'searched_by': '',
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
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.first().auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        
        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有600min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': lesson_info.objects.get(lesson_title='test_lesson_1').id,
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
            'searched_by': '',
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
        self.assertIn(f'"booked_time": ["3", "4"]', str(response.content, "utf8"))
        # self.fail(str(response.content, "utf8"))
        self.assertIn(f'"booked_status": "to_be_confirmed"', str(response.content, "utf8"))

        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'searched_by': '',
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
            'searched_by': '',
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
            'searched_by': '',
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
            'searched_by': '',
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
            'searched_by': '',
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
            'searched_by': '',
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
        self.assertEquals(5, str(response.content, "utf8").count('student_thumbnail_path'),
        str(response.content, "utf8")) # 並且總共有5筆資料

        # 此時帶入學生2號
        purchase_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                teacher_auth_id = teacher_profile.objects.first().auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

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
            'searched_by': '',
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
            'searched_by': '',
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
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        self.assertIn('success', str(response.content, "utf8"), 
        f"{lesson_info.objects.values()}\n {lesson_sales_sets.objects.values()}")

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.first().auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

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
            'searched_by': '',
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
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': 'no_discount',
            'total_amount_of_the_sales_set': 800,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'no_discount',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        
        the_purchase_object = \
            student_purchase_record.objects.get(id=2)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有60min的可用時數
        # print(f'student_remaining_minutes_of_each_purchased_lesson_set.XX {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        self.assertEquals(
            60,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(lesson_sales_set_id=2).available_remaining_minutes,
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
            'searched_by': '',
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
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object = \
            student_purchase_record.objects.get(id=3)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生2應該有600min的可用時數
        # print(f'student_remaining_minutes_of_each_purchased_lesson_set.XX {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
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
            'searched_by': '',
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


    def test_searched_by_feature(self):
        # 測試搜尋功能是否運作正確
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # print(f"test_searched_by_feature  {student_purchase_record.objects.values()}")

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.first().auth_id,
                teacher_auth_id = teacher_profile.objects.first().auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有30min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'bookingDateTime': f'{self.available_date_2}:4;'
        }  # 預約 30min  >> 1門課
        self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師應該有1則 待確認 預約訊息

        # 加入學生 auth_id = 2，讓他購買第二門課
        purchase_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_2').id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(1300*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        # 學生說付款了
        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                teacher_auth_id = teacher_profile.objects.first().auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test_lesson_2').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(lesson_title='test_lesson_2').id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object = \
            student_purchase_record.objects.get(student_auth_id=student_profile.objects.get(id=2).auth_id)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()

        # 讓學生2預約2門課
        booking_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,  # 學生的auth_id
            'lessonID': lesson_info.objects.get(lesson_title='test_lesson_2').id,
            'bookingDateTime': f'{self.available_date_1}:1,2,4,5;'
        }  # 預約 120min  >> 2門課 >> 1,2 4,5
        self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師應該有2+1則 待確認 預約訊息

        # 測試搜尋功能是否正常，只能搜尋學生姓名(暱稱)或課程title
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'searched_by': student_profile.objects.get(id=2).nickname,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
            
        self.assertEquals(2, str(response.content, "utf8").count('"to_be_confirmed"')) 
        # 應該有2門 來自學生 2的 to_be_confirmed
        self.assertEquals(2, str(response.content, "utf8").count(f'"student_nickname": "{student_profile.objects.get(id=2).nickname}"')) 
        # 共2筆
        self.assertEquals(2, str(response.content, "utf8").count('"discount_price": "10:90"')) 
        # 共2筆

        booking_history_post_data['searched_by'] = 'bbaaccd'
        # 亂打一通
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
        self.assertIn('success', str(response.content, 'utf8'))
        self.assertIn('"data": []', str(response.content, 'utf8')) 

        booking_history_post_data['searched_by'] = lesson_info.objects.get(lesson_title='test_lesson_1').lesson_title
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"to_be_confirmed"'), str(response.content, "utf8")) 
        # 應該有1門 來自學生1的 to_be_confirmed

        booking_history_post_data['searched_by'] = lesson_info.objects.get(lesson_title='test_lesson_2').lesson_title
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
        self.assertEquals(2, str(response.content, "utf8").count('"to_be_confirmed"'), str(response.content, "utf8")) 
        # 應該有2門來自學生2的 to_be_confirmed


    def test_get_teacher_s_booking_history_has_new_arguments(self):
        # 測試有沒有抓到新的參數
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.first().auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

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

        # 測試搜尋功能是否正常，只能搜尋學生姓名(暱稱)或課程title
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'searched_by': student_profile.objects.first().nickname,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '',
            'registered_to_date': ''
        }  # 測試看看不要加日期應該也ok  
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
        # 檢查新參數是否有成功帶進來
        self.assertEquals(1, str(response.content, "utf8").count(f'"lesson_booking_info_id": {1}')) 
        self.assertEquals(1, str(response.content, "utf8").count('"discount_price": "trial"')) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_start_time"')) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_end_time"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_time_in_minutes"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"student_confirmed_deadline"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"student_auth_id": {student_profile.objects.get(id=1).auth_id}'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"remark"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"is_teacher_given_feedback"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"is_student_given_feedback"'))


    def test_get_teacher_s_booking_history_new_arguments_values_are_right(self):
        # 測試新的參數內容正確性
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

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
            path='/api/lesson/bookingLessons/', data=booking_post_data)  # 送出預約，此時老師應該有1則 待確認 預約訊息

        # 測試搜尋功能是否正常，只能搜尋學生姓名(暱稱)或課程title
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'searched_by': student_profile.objects.first().nickname,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '',
            'registered_to_date': ''
        }  # 測試看看不要加日期應該也ok  
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
        # 檢查新參數的值，因為目前沒有完課紀錄，所以完課相關回傳的字串應為空字串，布林值則為None
        
        self.assertEquals(1, str(response.content, "utf8").count(f'"booked_status": "to_be_confirmed"'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_start_time": ""'),
            str(response.content, "utf8")) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_end_time": ""'),
            str(response.content, "utf8")) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_time_in_minutes": ""'),
            str(response.content, "utf8")) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"student_confirmed_deadline": ""'),
            str(response.content, "utf8")) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"remark": ""'),
            str(response.content, "utf8")) 
        self.assertIn(f'"is_teacher_given_feedback": null', str(response.content, "utf8"))
        self.assertIn(f'"is_student_given_feedback": null', str(response.content, "utf8"))

        # 接下來來完課一下，看看值會不會產生變化，記得老師要先確認預約唷
        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來來完課
        start_time, end_time = datetime(2021, 1, 19, 20, 50), datetime(2021, 1, 19, 22, 40)
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        booking_history_post_data['filtered_by'] = '' # 這次不加條件，應該所有紀錄都會出來
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
        # 檢查新參數的值，因為目前只有老師確認完課，所以完課學生相關回傳的字串應為空字串，布林值則為None，其他都有值
        self.assertIn(f'"booked_status": "student_not_yet_confirmed"', str(response.content, "utf8"))
        self.assertIn(f'"teacher_declared_start_time": "20:50"', str(response.content, "utf8")) 
        self.assertIn(f'"teacher_declared_end_time": "22:40"', str(response.content, "utf8")) 
        self.assertIn(f'"teacher_declared_time_in_minutes": {int((end_time - start_time).seconds / 60)}', str(response.content, "utf8"))
        self.assertIn(f'"student_confirmed_deadline": "{date_function.today() + timedelta(days=3)}"', str(response.content, "utf8"))
        self.assertIn(f'"remark": ""', str(response.content, "utf8"))
        self.assertIn(f'"is_teacher_given_feedback": false', str(response.content, "utf8"))  # 此時雙方尚未進行評價
        self.assertIn(f'"is_student_given_feedback": false', str(response.content, "utf8"))  # 此時雙方尚未進行評價

        # 接下來測試一下預約取消
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(lesson_title='test_lesson_1').id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(lesson_title='test_lesson_1').id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        response = \
            self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        the_purchase_object = \
            student_purchase_record.objects.last()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有 600 min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_3}:1,2,3;{self.available_date_4}:1,3,4,5;'
        }  # 預約 210 min  >> 3門課 123 1 345

        self.client.post(
            path='/api/lesson/bookingLessons/', data=booking_post_data)  # 送出預約，此時老師應該有3則 待確認 預約訊息
        
        # 接下來老師取消其中的 123 預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': lesson_booking_info.objects.get(
                booking_date_and_time = f'{self.available_date_3}:1,2,3;').id,
            'bookingStatus': 'canceled'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 並且確認 1 與 345 預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': lesson_booking_info.objects.get(
                booking_date_and_time = f'{self.available_date_4}:1;').id,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        change_booking_status_post_data['bookingID'] = \
            lesson_booking_info.objects.get(booking_date_and_time = f'{self.available_date_4}:3,4,5;').id
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)

        # 測試課程取消後，能不能show出新參數的值，不搜尋關鍵字
        booking_history_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'searched_by': '',
            'filtered_by': 'canceled',
            'registered_from_date': '',
            'registered_to_date': ''
        }  # 測試看看不要加日期應該也ok  
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
        # 檢查新參數的值，因為目前沒有完課紀錄，所以完課相關回傳的字串應為空字串，布林值則為None
        
        self.assertEquals(1, str(response.content, "utf8").count(f'"success"'),
            str(response.content, "utf8"))  # 應該只回傳一個 預約訊息
        self.assertIn(f'"remaining_time": 390', str(response.content, "utf8"))  # 600 - 210 = 390
        self.assertIn(f'"booked_status": "canceled"', str(response.content, "utf8"))
        self.assertIn(f'"teacher_declared_start_time": ""', str(response.content, "utf8"))
        self.assertIn(f'"teacher_declared_end_time": ""', str(response.content, "utf8"))
        self.assertIn(f'"teacher_declared_time_in_minutes": ""', str(response.content, "utf8"))
        self.assertIn(f'"student_confirmed_deadline": ""', str(response.content, "utf8"))
        self.assertIn(f'"remark": "{date_function.today()}', str(response.content, "utf8"))
        self.assertEqual(
            f'{date_function.today()} 老師婉拒預約',
            lesson_booking_info.objects.get(booking_date_and_time = f'{self.available_date_3}:1,2,3;').remark,
            lesson_booking_info.objects.values())
        self.assertIn(f'"is_teacher_given_feedback": null', str(response.content, "utf8"))
        self.assertIn(f'"is_student_given_feedback": null', str(response.content, "utf8"))

        # 接下來換測試學生取消雙方已確認的預約課程
        change_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'bookingID': lesson_booking_info.objects.get(
                booking_date_and_time = f'{self.available_date_4}:3,4,5;').id,
            'bookingStatus': 'canceled'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 一樣只filter canceled，這時應該會有兩筆資料
        response = self.client.post(
            path='/api/lesson/getTeachersBookingHistory/', data=booking_history_post_data)
        self.assertEquals(2, str(response.content, "utf8").count(f'"remark": "{date_function.today()}'),
            str(response.content, "utf8"))  # 會看到兩個關於取消的remark
        self.assertEqual(
            f'{date_function.today()} 學生取消預定課程',
            lesson_booking_info.objects.get(booking_date_and_time = f'{self.available_date_4}:3,4,5;').remark,
            lesson_booking_info.objects.values())
        

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
            'regName': 'test_name_1',
            'regNickname': 'test_nickname_1',
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
        teacher_post_data['regName'] = 'test_name_2~~',
        teacher_post_data['regNickname'] = 'test_nickname_2~~',
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建了2個老師
        
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
            'userID': teacher_profile.objects.get(id=1).auth_id,   # 這是老師1的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test1111',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test11111',
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
            'userID': teacher_profile.objects.get(id=2).auth_id,   # 這是老師2的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test2222',
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

        self.available_date_11_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[10].date
        self.available_date_12_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[11].date
        self.available_date_13_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[12].date
        self.available_date_4_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[3].date
        self.available_date_15_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[14].date


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name1)
            shutil.rmtree('user_upload/students/' + self.test_student_name2)
            shutil.rmtree('user_upload/students/' + self.test_student_name3)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name1)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name2)
        except:
            pass


    def test_get_student_booking_history_exist(self):
        '''
        測試 回傳該名學生所有預約、課程的狀態 這支api 存在
        {
            userID (student_auth_id)
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
            'userID': student_profile.objects.first().auth_id,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2000-01-01',
            'registered_to_date': '2021-01-31'
        }

        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        
        self.assertEqual(response.status_code, 200, str(response.content, "utf8"))


    def test_get_student_s_booking_history_api_work_when_student_has_no_booking_history_at_all(self):
        booking_history_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'filtered_by': '',
            'searched_by': '',
            'registered_from_date': '2000-01-01',
            'registered_to_date': '2050-01-31'
        }

        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"data": []', str(response.content, "utf8"))


    def test_get_student_s_booking_history_api_work_when_student_auth_id_not_exist(self):
        booking_history_post_data = {
            'userID': 35,
            'filtered_by': '',
            'searched_by': '',
            'registered_from_date': '2000-01-01',
            'registered_to_date': '2021-01-31'
        }

        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        
        self.assertIn('failed', str(response.content, "utf8"))


    def test_get_student_s_booking_history_work_when_student_has_common_lessons_filtered_and_not(self):
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object = \
            student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id
            )
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有600min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:1,2,5;{self.available_date_2_t1}:1,2,3,4,5;{self.available_date_4_t1}:1,3,4;'
        }  # 預約 330min  >> 5門課

        self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時學生應該有5則 送出的 待確認預約訊息
        
        self.assertEquals(5, 
        lesson_booking_info.objects.filter(student_auth_id=student_profile.objects.get(id=1).auth_id).count(),
        lesson_booking_info.objects.values())
        
        booking_history_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'filtered_by': 'to_be_confirmed',
            'searched_by': '',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件

        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        
        # print(f'has_common_lessons_to_be_confirmed_1 {str(response.content, "utf8")}')
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_1_t1}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_2_t1}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_4_t1}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_status": "to_be_confirmed"', str(response.content, "utf8"))

        booking_history_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'filtered_by': '',
            'searched_by': '',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        } # 無篩選條件
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_1_t1}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_2_t1}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_4_t1}"', str(response.content, "utf8"))
        self.assertIn(f'"booked_status": "to_be_confirmed"', str(response.content, "utf8"))

        # 接下來取消兩門課，第二門跟第三門
        for booking_id_to_be_canceled in \
            [lesson_booking_info.objects.get(booking_date_and_time=f'{self.available_date_1_t1}:5;').id, 
            lesson_booking_info.objects.get(booking_date_and_time=f'{self.available_date_2_t1}:1,2,3,4,5;').id]:
            changing_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'bookingID': booking_id_to_be_canceled,
                'bookingStatus': 'canceled'
            }  # 換老師取消
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        
        booking_history_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'filtered_by': 'to_be_confirmed',
            'searched_by': '',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件篩 to_be_confirmed
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(3, str(response.content, "utf8").count('to_be_confirmed'),
        str(response.content, "utf8")) # 應該只有3門 to_be_confirmed
        self.assertEquals(3, str(response.content, "utf8").count('remaining_time'),
        str(response.content, "utf8")) # 並且總共只有3筆資料

        booking_history_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'filtered_by': 'canceled',
            'searched_by': '',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件篩 canceled
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(0, str(response.content, "utf8").count('to_be_confirmed'),
        str(response.content, "utf8")) # 應該只有0門 to_be_confirmed
        self.assertEquals(2, str(response.content, "utf8").count('canceled'),
        str(response.content, "utf8")) # 並且總共只有2筆 canceled

        changing_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': lesson_booking_info.objects.get(id=1).id,
            'bookingStatus': 'confirmed'
        }  # 接下來老師確認第一筆的預約
        self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        booking_history_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'filtered_by': 'confirmed',
            'searched_by': '',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件篩 confirmed
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"confirmed"'),
        str(response.content, "utf8")) # 應該只有1門 confirmed
        self.assertEquals(1, str(response.content, "utf8").count('remaining_time'),
        str(response.content, "utf8")) # 並且總共只有1筆資料

        booking_history_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'filtered_by': '',
            'searched_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2011-01-01'
        }  # 測試沒篩選條件篩  選擇古老的日期
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(0, str(response.content, "utf8").count('"confirmed"'),
        str(response.content, "utf8")) # 應該只有0門 confirmed
        self.assertEquals(0, str(response.content, "utf8").count('remaining_time'),
        str(response.content, "utf8")) # 並且總共只有0筆資料

        booking_history_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'filtered_by': '',
            'searched_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試沒篩選條件篩  >> 這時應該有 confirmed_1, canceled_2, to_be_confirmed_2, 
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"confirmed"'),
        str(response.content, "utf8")) # 應該只有1門 confirmed
        self.assertEquals(2, str(response.content, "utf8").count('"canceled"'),
        str(response.content, "utf8")) # 應該只有2門 canceled
        self.assertEquals(2, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該只有2門 to_be_confirmed
        self.assertEquals(5, str(response.content, "utf8").count('remaining_time'),
        str(response.content, "utf8")) # 並且總共有5筆資料
        self.assertEquals(5, str(response.content, "utf8").count('teacher_thumbnail_path'),
        str(response.content, "utf8")) # 並且總共有5筆資料

        # 此時帶入學生2號
        purchase_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'teacherID':teacher_profile.objects.get(id=1).auth_id,
            'lessonID':lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object = \
            student_purchase_record.objects.get(student_auth_id=student_profile.objects.get(id=2).auth_id)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生2應該有600min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_12_t2}:1,2,3,4,5;{self.available_date_4_t2}:1,2,3,4;'
        }  # 預約 270min  >> 2門課
        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師 會再加上 2 則待確認預約訊息，總共 >>
            # confirmed_1, canceled_2, to_be_confirmed_4
            # 學生1 總共 1則確認、2則取消、2則待確認 ；學生2 總共 2 則待確認
            # 而 {self.available_date_4_t2}:1,2,3,4; 與 {self.available_date_4_t1}:1,2,3,4;
            # 兩者時段是重複的
        
        booking_history_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'filtered_by': 'to_be_confirmed',
            'searched_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01'
        } 
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(2, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 學生2 應該有2門 to_be_confirmed

        # 接著讓老師接受學生2的 {self.available_date_4_t2}:1,2,3,4; 預約
        # 檢查學生1 是不是多了一筆 canceled

        booking_history_post_data = {
            'userID':student_profile.objects.get(id=1).auth_id,
            'filtered_by': 'to_be_confirmed',
            'searched_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01'
        } 
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 先確認一下學生1目前待確認的課程預約為何
        print(f'先確認一下學生1目前待確認的課程預約為何: {str(response.content, "utf8")}')
        # >> {"data": 
        # [{"booked_date": "2021-01-15", "booked_time": "3,4", "booked_status": "to_be_confirmed", "lesson_title": "test", "teacher_nickname": "test_nickname", "discount_price": "10:90", "remaining_time": 270}, 
        # {"booked_date": "2021-01-15", "booked_time": "1", "booked_status": "to_be_confirmed", "lesson_title": "test", "teacher_nickname": "test_nickname", "discount_price": "10:90", "remaining_time": 270}], 
        # "status": "success", "errCode": null, "errMsg": null}

        changing_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'bookingID': lesson_booking_info.objects.filter(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                booking_date_and_time = f'{self.available_date_4_t2}:1,2,3,4;'
                ).first().id,
            'bookingStatus': 'confirmed'
        }  # 接下來老師確認第一筆的預約
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=changing_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        print(f'學生2的課程被老師確認一門預約： {self.available_date_4_t2}:1,2,3,4;')
        # 2021-01-15:1,2,3,4;
        # 對照往上13~14行，學生1會被取消2門課程
        
        # 此時學生2應該有1筆confirmed，1筆 to_be_confirmed
        booking_history_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01',
            'searched_by': ''
        } 
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 學生2 應該剩1門 to_be_confirmed

        booking_history_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'filtered_by': 'confirmed',
            'searched_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01'
        } 
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(1, str(response.content, "utf8").count('"confirmed"'),
        str(response.content, "utf8")) # 學生2 應該有1門 confirmed

        # 然後學生1 應該多了2筆 canceled，變成4筆

        booking_history_post_data = {
            'userID':student_profile.objects.get(id=1).auth_id,
            'filtered_by': 'canceled',
            'searched_by': '',
            'registered_from_date': '2010-01-01',
            'registered_to_date': '2050-01-01'
        } 
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(4, str(response.content, "utf8").count('"canceled"'),
        str(response.content, "utf8")) # 學生1 應該有3門 canceled，變成4筆


    def test_get_student_s_booking_history_work_when_student_has_trial_and_no_discount_lessons_filtered_and_not(self):
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(id=1).id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有30min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2_t1}:4;'
        }  # 預約 30min  >> 1門課

        self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時學生應該有1則送出的 待確認 預約訊息

        self.assertEquals(1, 
        lesson_booking_info.objects.filter(student_auth_id=student_profile.objects.first().auth_id).count(),
        lesson_booking_info.objects.values())
        
        booking_history_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'searched_by': '',
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn(f'"booked_date": "{self.available_date_2_t1}"', str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該只有1門 to_be_confirmed
        self.assertEquals(1, str(response.content, "utf8").count('"booked_time"'),
        str(response.content, "utf8")) # 共1筆
        self.assertIn(f'"discount_price": "trial"', str(response.content, "utf8"))
        

        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(id=1).id,
            'sales_set': 'no_discount',
            'total_amount_of_the_sales_set': 800,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'no_discount',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        
        the_purchase_object = \
            student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.first().auth_id,
                lesson_sales_set_id = lesson_sales_sets.objects.filter(
                    lesson_id = 1,
                    sales_set = 'no_discount'
                ).first().id
            )
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有60min的可用時數
        # print(f'student_remaining_minutes_of_each_purchased_lesson_set.XX {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        self.assertEquals(
            60,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                lesson_sales_set_id=lesson_sales_sets.objects.filter(lesson_id=1, sales_set='no_discount').first().id
                ).available_remaining_minutes,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values())

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_3_t1}:4;{self.available_date_1_t1}:1;'
        }  # 預約 60min  >> 2門課

        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師與學生1應該各有有3則 待確認 預約訊息
        self.assertIn('success', str(response.content, 'utf8'))

        booking_history_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'searched_by': '',
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(3, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該有3門 to_be_confirmed
        self.assertEquals(3, str(response.content, "utf8").count('"booked_time"'),
        str(response.content, "utf8")) # 共3筆
        self.assertEquals(2, str(response.content, "utf8").count('"discount_price": "no_discount"'),
        str(response.content, "utf8")) # 共2筆
        self.assertEquals(1, str(response.content, "utf8").count('"discount_price": "trial"'),
        str(response.content, "utf8")) # 共1筆
        print(f'確認加入學生2前，學生1目前的課程預約日: {str(response.content, "utf8")}')

        # 加入學生 auth_id = 2
        purchase_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        the_purchase_object = \
            student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                lesson_sales_set_id = lesson_sales_sets.objects.filter(
                    lesson_id = 1,
                    sales_set = '10:90'
                ).first().id
            )

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=2).auth_id,
                teacher_auth_id = lesson_info.objects.get(id=1).teacher.auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '10:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生2應該有600min的可用時數
        # print(f'student_remaining_minutes_of_each_purchased_lesson_set.XX {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        self.assertEquals(
            600,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                student_auth_id=student_profile.objects.get(id=2).auth_id).available_remaining_minutes,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values())

        booking_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_13_t2}:4,5;{self.available_date_11_t2}:1,2,3,5;'
        }  # 預約 180min  >> 3門課
        
        response = self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師應該總共有6則 待確認 預約訊息，其中3門來自學生2
        self.assertIn('success', str(response.content, 'utf8'))

        booking_history_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'searched_by': '',
            'filtered_by': '',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試無篩選條件
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', 
            data=booking_history_post_data)
        self.assertEquals(3, str(response.content, "utf8").count('"to_be_confirmed"'),
        str(response.content, "utf8")) # 應該有3門 to_be_confirmed
        self.assertEquals(3, str(response.content, "utf8").count('"booked_time"'),
        str(response.content, "utf8")) # 共3筆
        self.assertEquals(3, str(response.content, "utf8").count('"discount_price": "10:90"'),
        str(response.content, "utf8")) # 共3筆
        self.assertEquals(3, str(response.content, "utf8").count('"remaining_time": 420'),
        str(response.content, "utf8")) # 共3筆
        print(f'確認學生2目前的課程預約日: {str(response.content, "utf8")}')


    def test_searched_by_feature(self):
        '''
        測試 學生學習檔案 這隻API的搜尋功能是否運作正確
        '''
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(lesson_title='test11111').id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test11111').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    lesson_id = lesson_info.objects.get(lesson_title='test11111').id,
                    is_open = True
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        response = \
            self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有30min的可用時數
        self.assertEqual(1,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.count(),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values())

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2_t1}:4;'
        }  # 預約 30min  >> 1門課
        response = self.client.post(
            path='/api/lesson/bookingLessons/', data=booking_post_data)  # 送出預約，此時老師應該有1則 待確認 預約訊息
        self.assertIn('success', str(response.content, "utf8"))

        # 讓學生 auth_id = 1，購買第二位老師的第二門課
        purchase_post_data = {
            'userID':student_profile.objects.get(id=1).auth_id,
            'teacherID':teacher_profile.objects.get(id=2).auth_id,
            'lessonID':lesson_info.objects.get(lesson_title='test2222').id,
            'sales_set': '5:90',
            'total_amount_of_the_sales_set': int(1200*5*0.9),
            'q_discount':0}
        response = self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=2).auth_id,
                lesson_id = lesson_info.objects.get(lesson_title='test2222').id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '5:90',
                    lesson_id = lesson_info.objects.get(lesson_title='test2222').id,
                    is_open = True
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        
        response = \
            self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        the_purchase_object = \
            student_purchase_record.objects.get(teacher_auth_id=teacher_profile.objects.get(id=2).auth_id)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()

        self.assertEqual(2,
            student_remaining_minutes_of_each_purchased_lesson_set.objects.count(),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values())

        # 讓學生1預約2門課
        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': lesson_info.objects.get(lesson_title='test2222').id,
            'bookingDateTime': f'{self.available_date_1_t1}:1,2,4,5;'
        }  # 預約 120min  >> 2門課 >> 1,2 4,5
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)  # 送出預約，此時老師應該有3則 待確認 預約訊息
        self.assertIn('success', str(response.content, "utf8"))

        # 測試搜尋功能是否正常，只能搜尋老師姓名(暱稱)或課程title
        booking_history_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'searched_by': teacher_profile.objects.get(id=2).nickname,
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '2020-01-01',
            'registered_to_date': '2050-01-01'
        }  # 測試有篩選條件
        response1 = self.client.post(path='/api/lesson/getStudentsBookingHistory/', data=booking_history_post_data)
        self.assertEquals(2, str(response1.content, "utf8").count('"to_be_confirmed"'),
            lesson_booking_info.objects.values().filter(student_auth_id=student_profile.objects.first().auth_id)) 
        # 應該有2門 來自學生預定老師2的to_be_confirmed

        self.assertIn(f'"{teacher_profile.objects.get(id=2).nickname}"',
            str(response1.content, "utf8"))
        # 應該出現老師2
        self.assertNotIn(f'"{teacher_profile.objects.get(id=1).nickname}"',
            str(response1.content, "utf8"))
        # 不應該出現老師1

        booking_history_post_data['searched_by'] = 'bbaa但ccd'
        # 亂打一通
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', data=booking_history_post_data)
        self.assertIn('success', str(response.content, 'utf8'))
        self.assertIn('"data": []', str(response.content, 'utf8')) 

    
    def test_get_student_s_booking_history_has_new_arguments(self):
        '''
        測試 學生學習檔案 這隻API修改後 有沒有抓到新的參數
        '''
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(id=1).id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.first().auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有30min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2_t1}:4;'
        }  # 預約 30min  >> 1門課

        self.client.post(
            path='/api/lesson/bookingLessons/',
            data=booking_post_data)  # 送出預約，此時老師應該有1則 待確認 預約訊息

        # 只列出待確認的預約
        booking_history_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'searched_by': '',
            'filtered_by': 'to_be_confirmed',
            'registered_from_date': '',
            'registered_to_date': ''
        }  # 測試看看不要加日期應該也ok  
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', data=booking_history_post_data)
        # 檢查新參數是否有成功帶進來
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn(f'"teacher_auth_id": {teacher_profile.objects.first().auth_id}', str(response.content, "utf8"))
        self.assertIn(f'"teacher_nickname": "{teacher_profile.objects.first().nickname}"', str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count(f'"lesson_booking_info_id": 1'))
        self.assertEquals(1, str(response.content, "utf8").count('"discount_price": "trial"')) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_start_time"')) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_end_time"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_time_in_minutes"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"student_confirmed_deadline"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"remark"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"is_teacher_given_feedback"'))
        self.assertEquals(1, str(response.content, "utf8").count(f'"is_student_given_feedback"'))


    
    def test_get_student_s_booking_history_new_arguments_values_are_right(self):
        # 測試新的參數內容正確性
        # 學生1先購買一門老師1的試教課
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.get(id=1).id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=1).auth_id,
                lesson_id = lesson_info.objects.get(id=1).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = 'trial',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(id=1).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有30min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2_t1}:4;'
        }  # 預約 30min  >> 1門課

        self.client.post(
            path='/api/lesson/bookingLessons/', data=booking_post_data)  # 送出預約，此時老師應該有1則 待確認 預約訊息

        # 不加任何條件
        booking_history_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'searched_by': '',
            'filtered_by': '',
            'registered_from_date': '',
            'registered_to_date': ''
        }  # 測試看看不要加日期應該也ok  
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', data=booking_history_post_data)
        # 檢查新參數的值，因為目前沒有完課紀錄，所以完課相關回傳的字串應為空字串，布林值則為None
        
        self.assertEquals(1, str(response.content, "utf8").count(f'"booked_status": "to_be_confirmed"'),
            str(response.content, "utf8"))
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_start_time": ""'),
            str(response.content, "utf8")) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_end_time": ""'),
            str(response.content, "utf8")) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"teacher_declared_time_in_minutes": ""'),
            str(response.content, "utf8")) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"student_confirmed_deadline": ""'),
            str(response.content, "utf8")) 
        self.assertEquals(1, str(response.content, "utf8").count(f'"remark": ""'),
            str(response.content, "utf8")) 
        self.assertIn(f'"is_teacher_given_feedback": null', str(response.content, "utf8"))
        self.assertIn(f'"is_student_given_feedback": null', str(response.content, "utf8"))

        # 接下來來完課一下，看看值會不會產生變化，記得老師要先確認預約唷
        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來來完課
        start_time, end_time = datetime(2021, 1, 19, 20, 50), datetime(2021, 1, 19, 22, 40)
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 重送一次
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', data=booking_history_post_data)
        # 檢查新參數的值，因為目前只有老師確認完課，所以完課學生相關回傳的字串應為空字串，布林值則為None，其他都有值
        self.assertIn(f'"booked_status": "student_not_yet_confirmed"', str(response.content, "utf8"))
        self.assertIn(f'"teacher_declared_start_time": "20:50"', str(response.content, "utf8")) 
        self.assertIn(f'"teacher_declared_end_time": "22:40"', str(response.content, "utf8")) 
        self.assertIn(f'"teacher_declared_time_in_minutes": {int((end_time - start_time).seconds / 60)}', str(response.content, "utf8"))
        self.assertIn(f'"student_confirmed_deadline": "{date_function.today() + timedelta(days=3)}"', str(response.content, "utf8"))
        self.assertIn(f'"remark": ""', str(response.content, "utf8"))
        self.assertIn(f'"is_teacher_given_feedback": false', str(response.content, "utf8"))  # 此時雙方尚未進行評價
        self.assertIn(f'"is_student_given_feedback": false', str(response.content, "utf8"))  # 此時雙方尚未進行評價

        # 接下來測試一下預約取消，向第二個老師購課
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.get(id=2).auth_id,
            'lessonID':lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id,
            'sales_set': '5:90',
            'total_amount_of_the_sales_set': int(1200*5*.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(
                student_auth_id = student_profile.objects.get(id=1).auth_id,
                teacher_auth_id = teacher_profile.objects.get(id=2).auth_id,
                lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id,
                lesson_sales_set_id = lesson_sales_sets.objects.get(
                    sales_set = '5:90',
                    is_open = True,
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).id
            ).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}  # 學生跟Quikok確認付款
        response = \
            self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        the_purchase_object = \
            student_purchase_record.objects.last()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了，所以 學生1應該有 600 min的可用時數

        booking_post_data = {
            'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
            'lessonID': lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id,
            'bookingDateTime': f'{self.available_date_13_t2}:1,2,3;{self.available_date_4_t2}:1,3,4,5;'
        }  # 預約 210 min  >> 3門課 123 1 345

        self.client.post(
            path='/api/lesson/bookingLessons/', data=booking_post_data)  # 送出預約，此時老師應該有3則 待確認 預約訊息
        
        # 接下來老師取消其中的 123 預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=2).auth_id,
            'bookingID': lesson_booking_info.objects.get(
                booking_date_and_time = f'{self.available_date_13_t2}:1,2,3;').id,
            'bookingStatus': 'canceled'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 並且確認 1 與 345 預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=2).auth_id,
            'bookingID': lesson_booking_info.objects.get(
                booking_date_and_time = f'{self.available_date_4_t2}:1;').id,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        change_booking_status_post_data['bookingID'] = \
            lesson_booking_info.objects.get(booking_date_and_time = f'{self.available_date_4_t2}:3,4,5;').id
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)

        # 測試課程取消後，能不能show出新參數的值，不搜尋關鍵字
        booking_history_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'searched_by': '',
            'filtered_by': 'canceled',
            'registered_from_date': '',
            'registered_to_date': ''
        }  # 測試看看不要加日期應該也ok  
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', data=booking_history_post_data)
        # 檢查新參數的值，因為目前沒有完課紀錄，所以完課相關回傳的字串應為空字串，布林值則為None
        
        self.assertEquals(1, str(response.content, "utf8").count(f'"success"'),
            str(response.content, "utf8"))  # 應該只回傳一個 預約訊息
        self.assertIn(f'"booked_status": "canceled"', str(response.content, "utf8"))
        self.assertIn(f'"teacher_declared_start_time": ""', str(response.content, "utf8"))
        self.assertIn(f'"teacher_declared_end_time": ""', str(response.content, "utf8"))
        self.assertIn(f'"teacher_declared_time_in_minutes": ""', str(response.content, "utf8"))
        self.assertIn(f'"student_confirmed_deadline": ""', str(response.content, "utf8"))
        self.assertIn(f'"remark": "{date_function.today()}', str(response.content, "utf8"))
        self.assertEqual(
            f'{date_function.today()} 老師婉拒預約',
            lesson_booking_info.objects.get(booking_date_and_time = f'{self.available_date_13_t2}:1,2,3;').remark,
            lesson_booking_info.objects.values())
        self.assertIn(f'"is_teacher_given_feedback": null', str(response.content, "utf8"))
        self.assertIn(f'"is_student_given_feedback": null', str(response.content, "utf8"))

        # 接下來換測試學生取消雙方已確認的預約課程
        change_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'bookingID': lesson_booking_info.objects.get(
                booking_date_and_time = f'{self.available_date_4_t2}:3,4,5;').id,
            'bookingStatus': 'canceled'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 一樣只filter canceled，這時應該會有兩筆資料
        response = self.client.post(
            path='/api/lesson/getStudentsBookingHistory/', data=booking_history_post_data)
        self.assertEquals(2, str(response.content, "utf8").count(f'"remark": "{date_function.today()}'),
            str(response.content, "utf8"))  # 會看到兩個關於取消的remark
        self.assertEqual(f'{date_function.today()} 學生取消預定課程',
            lesson_booking_info.objects.get(booking_date_and_time = f'{self.available_date_4_t2}:3,4,5;').remark,
            lesson_booking_info.objects.values())


class CLASS_FINISHED_TEST(TestCase):
    '''
    用來測試完課API是否運作如常
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
            'regName': 'test_name_1',
            'regNickname': 'test_nickname_1',
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
        teacher_post_data['regName'] = 'test_name_2~~',
        teacher_post_data['regNickname'] = 'test_nickname_2~~',
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建了2個老師
        
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
            'userID': teacher_profile.objects.get(id=1).auth_id,   # 這是老師1的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test1111',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test11111',
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
            'userID': teacher_profile.objects.get(id=2).auth_id,   # 這是老師2的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test2222',
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

        self.available_date_11_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[10].date
        self.available_date_12_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[11].date
        self.available_date_13_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[12].date
        self.available_date_4_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[3].date
        self.available_date_15_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[14].date


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name1)
            shutil.rmtree('user_upload/students/' + self.test_student_name2)
            shutil.rmtree('user_upload/students/' + self.test_student_name3)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name1)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name2)
        except:
            pass


    def test_lesson_completed_notification_from_teacher_exist(self):
        # 確認連結存在
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': '10:20',
                'end_time': '11:20',
                'time_interval_in_minutes': 60
        }
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertEqual(200, response.status_code)

    
    def test_lesson_completed_notification_from_teacher_check_if_had_correspondant_booking_info(self):
        '''
        確認當有對應的預約時段時，可以進行完課的動作，若沒有對應的預約時段，則不行
        '''
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': '10:20',
                'end_time': '11:20',
                'time_interval_in_minutes': 60
        }  # 測試看看這個 api 能不能產出對應的 record 來
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        # 因為沒有對應的預約紀錄，所以沒辦法完課

        # 接下來來產生對應的預約，先進行購課
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount': 0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertEqual(1, student_purchase_record.objects.count())

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        self.assertEqual('reconciliation',
            student_purchase_record.objects.get(id=1).payment_status)
        # 此時，學生通知我們她已經完成付款
        # student_purchase_record.objects.filter(id=1).update(payment_status='paid')
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了
        self.assertEqual('paid',
            student_purchase_record.objects.get(id=1).payment_status)

        #print(f"student_purchase_record: {student_purchase_record.objects.values()}")
        #print(f"student_remaining: {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}")

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:1,2,3,4;'} 
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 預約成功

        # 接著老師進行完課
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': '10:20',
                'end_time': '11:20',
                'time_interval_in_minutes': 60
        }  # 測試看看這個 api 能不能產出對應的 record 來
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        # 因為沒有經雙方確認的預約，因此無法進行完課
        self.assertIn('"errCode": "3"', str(response.content, "utf8"))

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 此時應該可以進行完課動作惹
        # 接著老師進行完課
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': '10:20',
                'end_time': '11:20',
                'time_interval_in_minutes': 60
        }  # 測試看看這個 api 能不能產出對應的 record 來
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))


    def test_lesson_completed_notification_from_teacher_create_record_in_the_table(self):
        '''
        確認當老師按完課後，會產生對應的紀錄
        '''
        # 先進行購課
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount': 0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        # student_purchase_record.objects.filter(id=1).update(payment_status='paid')
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了
        self.assertEqual('paid',
            student_purchase_record.objects.get(id=1).payment_status)

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:1,2,3,4;'} 
            # 預約了120分鐘
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 預約成功

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 此時應該可以進行完課動作惹
        # 接著老師進行完課
        start_time, end_time = datetime(2021, 1, 19, 20, 50), datetime(2021, 1, 19, 22, 40)
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 檢查 lesson_completed_record 是否產生對應的紀錄
        self.assertEqual(1, lesson_completed_record.objects.count())
        # 測試booking_time計算正確
        self.assertEqual(
            int(len(lesson_booking_info.objects.get(id=1).booking_date_and_time[:-1].split(':')[1].split(','))) * 30,
            lesson_completed_record.objects.get(id=1).booking_time_in_minutes,
            lesson_completed_record.objects.values())

        # 測試時間計算正不正確
        self.assertEqual(
            (
                120,
                int((end_time - start_time).seconds / 60),
                date_function.today() + timedelta(days=3),
                start_time.strftime("%H:%M"),
                end_time.strftime("%H:%M")
            ),
            (
                lesson_completed_record.objects.get(id=1).booking_time_in_minutes,
                lesson_completed_record.objects.get(id=1).teacher_declared_time_in_minutes,
                lesson_completed_record.objects.get(id=1).student_confirmed_deadline,
                lesson_completed_record.objects.get(id=1).teacher_declared_start_time.strftime('%H:%M'),
                lesson_completed_record.objects.get(id=1).teacher_declared_end_time.strftime('%H:%M')
            ),
        lesson_completed_record.objects.values())

    @skip
    def test_send_email_to_student_and_teacher_when_lesson_completed(self):
        '''
        確認當老師按完課後，學生會收到通知信來確認這個時數是否正確、老師會收到信叫他寫評價
        '''
        # 0203:先skip是因為email改用thread寄, 尚不曉得該用甚麼方法test...
        # 先進行購課
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount': 0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        # student_purchase_record.objects.filter(id=1).update(payment_status='paid')
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了
        self.assertEqual('paid',
            student_purchase_record.objects.get(id=1).payment_status)

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:1,2,3,4;'} 
            # 預約了120分鐘
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 預約成功

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        mail.outbox = []
        # 此時應該可以進行完課動作惹
        # 接著老師進行完課
        start_time, end_time = datetime(2021, 1, 19, 20, 50), datetime(2021, 1, 19, 22, 40)
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 檢查 lesson_completed_record 是否產生對應的紀錄
        self.assertEqual(1, lesson_completed_record.objects.count())
        # 檢查是否收到通知信
        self.assertEqual(mail.outbox[0].subject, 'Quikok!開課通知：老師請你確認上課時數囉!')
        self.assertEqual(mail.outbox[1].subject, 'Quikok!開課通知：給學生的評價填了嗎~')

    def test_lesson_completed_confirmation_from_student_exist(self):
        # 確認學生確認完課通知的連結存在
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'
        }
        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertEqual(200, response.status_code)

    
    def test_lesson_completed_confirmation_from_student_updates_lesson_completed_record(self):
        '''
        確認當學生進行完課確認時，會更新相關的 lesson_completed_record 的紀錄
        '''
        # 先測試當老師沒有發送完課通知前，這個api不能被啟動
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'
        }
        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('failed', str(response.content, "utf8"))

        # 接著測試學生確認時數
        # 先購買課程
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(800*10*0.9),
            'q_discount': 0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:1,2,3,4;'} 
            # 預約了120分鐘
        self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 0, 30)
        end_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 2, 30)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': '2021-01-01',
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)

        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=1).booking_status)

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'}
        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 確認資料庫也有同步更新

        self.assertEqual(
            (
                'finished',  # 因為學生也確認課程時數無誤，此時對應的狀態為 finished
                False,  # 學生未反對老師的時數
                True,  # 學生同意老師的時數
                False  # 不是由Quikok進行確認的
            ),
            (
                lesson_booking_info.objects.get(id=1).booking_status,
                lesson_completed_record.objects.get(id=1).is_student_disagree_with_teacher_s_declared_time,
                lesson_completed_record.objects.get(id=1).is_student_confirmed,
                lesson_completed_record.objects.get(id=1).confirmed_by_quikok
            ),
            f'\nlesson_booking_info:\n{lesson_booking_info.objects.values()}\n\nlesson_completed_record:\n{lesson_completed_record.objects.values()}'
        )

        # 接下來測試若學生不同意老師宣稱的時數時，相關的狀態會不會更改
        # 再來重新預約、完課的過程吧
        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_3_t1}:2,3,4,5;'} 
            # 預約了120分鐘
        self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': \
                lesson_booking_info.objects.get(booking_date_and_time=f'{self.available_date_3_t1}:2,3,4,5;').id,
            'bookingStatus': 'confirmed'}
        self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)

        # 接著老師進行完課
        start_time, end_time = datetime(2021, 1, 19, 1, 50), datetime(2021, 1, 19, 5, 40)
        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': \
                    lesson_booking_info.objects.get(booking_date_and_time=f'{self.available_date_3_t1}:2,3,4,5;').id,
                'lesson_date': self.available_date_3_t1,
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        current_test_booking_id = \
            lesson_booking_info.objects.get(booking_date_and_time=f'{self.available_date_3_t1}:2,3,4,5;').id
        # 此時，學生應該可以進行抗議了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': current_test_booking_id,
            'action': 'disagree'}
        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 確認資料庫也有同步更新
        self.assertEqual(
            (
                'quikok_dealing_for_student_disagreed',  # 因為課程時數無誤有爭議，此時對應的狀態為 quikok_dealing_for_student_disagreed
                True,  # 學生反對老師的時數
                False,  # 學生不同意老師的時數
                False  # 不是由Quikok進行確認的，因為爭議還在處理中
            ),
            (
                lesson_booking_info.objects.get(id=current_test_booking_id).booking_status,
                lesson_completed_record.objects.get(id=current_test_booking_id).is_student_disagree_with_teacher_s_declared_time,
                lesson_completed_record.objects.get(id=current_test_booking_id).is_student_confirmed,
                lesson_completed_record.objects.get(id=current_test_booking_id).confirmed_by_quikok
            ),
            f'\nlesson_booking_info:\n{lesson_booking_info.objects.values()}\n\nlesson_completed_record:\n{lesson_completed_record.objects.values()}'
        )


    def test_if_withholding_times_updated_after_trial_lesson_completed(self):
        '''
        這個用來測試當 試教 課程確認結束後，假設時間如預約時間，學生的時數會不會正確被更新。
        '''
        # 先購買課程
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:1;'} 
            # 預約了30分鐘  00:30 - 01:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 0, 30)
        end_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 1, 30)
        # 超時30分鐘，但因為是試教，所以沒關係

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來

        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=1).booking_status)

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'}

        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來測試學生的預扣時數是否有被扣除
        self.assertEqual(
            (
                0,  # 預扣時數此時應該為0
                30  # 已消耗的時數此時應該為120
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).confirmed_consumed_minutes
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )

    
    def test_if_withholding_times_updated_after_common_lesson_completed(self):
        '''
        這個用來測試當 一般 課程確認結束後，假設時間如預約時間，學生的時數會不會正確被更新。
        '''
        # 先購買 no_discount
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': 'no_discount',
            'total_amount_of_the_sales_set': 800,
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 確認一下可用時數是不是60分鐘
        self.assertEqual(60, student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.values())


        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:3,4;'} 
            # 預約了30分鐘  01:30 - 02:30
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 1, 30)
        end_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 2, 30)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來

        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=1).booking_status)

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'}

        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來測試學生的預扣時數是否有被扣除
        self.assertEqual(
            (
                0,  # 預扣時數此時應該為 0
                60  # 已消耗的時數此時應該為 60
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).confirmed_consumed_minutes
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )

        # 接下來測試購買 老師2 的 5:90 方案
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=2).auth_id,
            'lessonID': lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id,
            'sales_set': '5:90',
            'total_amount_of_the_sales_set': int(5*1200*0.9),
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=2).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=2)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id,
            'bookingDateTime': f'{self.available_date_11_t2}:1,2,3,4,5;'} 
            # 預約了150分鐘  00:30 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=2).auth_id,
            'bookingID': 2,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_11_t2.year, self.available_date_11_t2.month, self.available_date_11_t2.day, 0, 30)
        end_time = \
            datetime(self.available_date_11_t2.year, self.available_date_11_t2.month, self.available_date_11_t2.day, 3, 0)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=2).auth_id,
                'lesson_booking_info_id': 2,
                'lesson_date': str(self.available_date_11_t2),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來

        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=2).booking_status)

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 2,
            'action': 'agree'}

        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來測試學生的預扣時數是否有被扣除
        self.assertEqual(
            (
                5  * 60 - 150,
                0,  # 預扣時數此時應該為 0
                150  # 已消耗的時數此時應該為 60
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 購買第二次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 購買第二次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 購買第二次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).confirmed_consumed_minutes
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )

        # 接下來測試跨方案能不能扣時數成功
        # 這次購買 老師2 的 30:70 方案
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=2).auth_id,
            'lessonID': lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id,
            'sales_set': '30:70',
            'total_amount_of_the_sales_set': int(30*1200*0.7),
            'q_discount': 0}  # 測試看看其中2萬元是Q幣支付的會怎麼樣
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        # self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=3).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=3)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id,
            'bookingDateTime': f'{self.available_date_12_t2}:0,1,2,3,4,5;{self.available_date_4_t2}:3,4,5;'} 
            # 預約了270分鐘  00:00 - 03:00 // 180    01:30 - 03:00  // 90
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 讓老師確認學生的預約 - 1/2
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=2).auth_id,
            'bookingID': 3,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 讓老師確認學生的預約 - 2/2
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=2).auth_id,
            'bookingID': 4,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # =========================== 接著老師進行完課 1/2 ===========================
        start_time = \
            datetime(self.available_date_12_t2.year, self.available_date_12_t2.month, self.available_date_12_t2.day, 0, 0)
        end_time = \
            datetime(self.available_date_12_t2.year, self.available_date_12_t2.month, self.available_date_12_t2.day, 3, 0)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=2).auth_id,
                'lesson_booking_info_id': 3,
                'lesson_date': str(self.available_date_12_t2),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來

        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=3).booking_status)

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 3,
            'action': 'agree'}

        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來測試學生的預扣時數是否有被扣除
        self.assertEqual(
            (
                0,  # 第二次購買的可用時數現在應該為 0
                0,  # 第二次購買的預扣時數此時應該也為 0
                300,  # 第二次購買的已消耗時數此時應該為 300
                30 * 60 - 120,  # 第三次購買的可用時數現在應該為完整的減掉 120 分鐘的預約
                90,  # 第三次購買的預扣時數
                30  # 第三次購買的已消耗時數
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 購買第二次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 購買第二次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 購買第二次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).confirmed_consumed_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 3,  # 購買第三次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 3,  # 購買第三次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 3,  # 購買第三次
                    lesson_id = lesson_info.objects.get(teacher=teacher_profile.objects.get(id=2)).id
                ).confirmed_consumed_minutes
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )


    def test_if_withholding_times_updated_after_common_lesson_completed_greater_than_booking_time(self):
        '''
        這個用來測試當 一般 課程確認結束後，假設時間比預約時間來得更長，學生的時數會不會正確被更新。
        '''
        # 先購買 老師1 的 10:90
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(10*800*.9),
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:0,1,2,3,4,5;'} 
            # 預約了180分鐘  00:00 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        print(f'inner info {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課，完課時間比預期的多出1小時，共計4小時
        start_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 0, 0)
        end_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 4, 0)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來

        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=1).booking_status)

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'}
        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來測試學生的預扣時數是否有正確被扣除
        self.assertEqual(
            (
                10 * 60 - 4 * 60,  # 可用時數應該為原先購買的時數減掉4小時
                0,  # 預扣時數此時應該為 0 ，因為沒有其他的預約了
                240  # 已消耗的時數此時應該為原先的 180 分鐘 + 額外的 60 分鐘 = 240 分鐘
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).confirmed_consumed_minutes
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )

        # 接著再進行一次完課，看超時且學生可用時數(目前還剩360分)不足以扣除時，會不會出現 student_owing_teacher_time 的紀錄
        # 接著讓學生再次進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2_t1}:0,1,2,3,4,5;'} 
            # 一樣預約180分鐘  00:00 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # print(f'inner info {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 2,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課，完課時間比預期的3小時多出130分鐘，共計 3 * 60 + 130 = 410 分鐘，超出可用時數的360分鐘
        start_time = \
            datetime(self.available_date_2_t1.year, self.available_date_2_t1.month, self.available_date_2_t1.day, 0, 0)
        end_time = \
            datetime(self.available_date_2_t1.year, self.available_date_2_t1.month, self.available_date_2_t1.day, 6, 50)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 2,
                'lesson_date': str(self.available_date_2_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來

        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=2).booking_status,
            lesson_booking_info.objects.values())

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 2,
            'action': 'agree'}
        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來測試學生的預扣時數是否有正確被扣除
        self.assertEqual(
            (
                0,  # 可用時數應該由剛剛的 360min 變成 0min 了
                0,  # 預扣時數此時應該為 0
                600  # 已消耗的時數此時應該為原先的 240 分鐘 變成全部扣完 >> 600 分鐘
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).confirmed_consumed_minutes
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )

        # 此時學生1 應該會多出50分鐘的欠時紀錄
        self.assertEqual(
            (
                1, 50
            ),
            (
                student_owing_teacher_time.objects.count(),
                student_owing_teacher_time.objects.first().owing_minutes
            ),
            
        )
        # print(f'inner info {student_owing_teacher_time.objects.values()}')

        # 接下來測試一下購買兩個方案是不是也一切順利
        # 購買 老師1 的 10:90 與 20:80
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(10*800*.9),
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=2).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=2)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '20:80',
            'total_amount_of_the_sales_set': int(20*800*.8),
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=3).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=3)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生再次進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_4_t1}:0,1,2,3,4,5;'} 
            # 一樣預約180分鐘  00:00 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # print(f'inner info {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 3,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課，因為目前共有 10小時 + 20小時 合計 30小時/1800分鐘
        # 完課時間長度設定為 680 分鐘，測試看看能不能跨方案扣除
        start_time = \
            datetime(self.available_date_4_t1.year, self.available_date_4_t1.month, self.available_date_4_t1.day, 0, 0)
        end_time = \
            datetime(self.available_date_4_t1.year, self.available_date_4_t1.month, self.available_date_4_t1.day, 11, 20)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 3,
                'lesson_date': str(self.available_date_4_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來

        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=3).booking_status,
            lesson_booking_info.objects.values())

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 3,
            'action': 'agree'}
        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來測試學生的預扣時數是否有正確被扣除
        self.assertEqual(
            (
                0,  # 第二次可用時數
                0,  # 第二次預扣時數此時應該為 0
                600,  # 第二次已消耗的時數此時應該全部扣完 >> 600 分鐘
                1200 - 80,  # 第三次可用時數
                0,  # 第三次預扣時數此時應該為 0
                80  # 第三次已消耗的時數
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 第二次
                    lesson_id = 1
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 第二次
                    lesson_id = 1
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 2,  # 第二次
                    lesson_id = 1
                ).confirmed_consumed_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 3,  # 第三次
                    lesson_id = 1
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 3,  # 第三次
                    lesson_id = 1
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 3,  # 第三次
                    lesson_id = 1
                ).confirmed_consumed_minutes
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )


    def test_if_withholding_times_updated_after_common_lesson_completed_less_than_booking_time(self):
        '''
        這個用來測試當 一般 課程確認結束後，假設時間比預約時間來得更短，學生的時數會不會正確被更新。
        '''
        # 先購買 老師1 的 10:90
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(10*800*.9),
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:0,1,2,3,4,5;'} 
            # 預約了180分鐘  00:00 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        print(f'inner info {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課，完課時間比預期的少40分鐘，共計 140 分鐘
        start_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 0, 0)
        end_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 2, 20)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來

        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 測試一下此時該完課紀錄所對應的預約狀態應該是  student_not_yet_confirmed
        self.assertEqual('student_not_yet_confirmed', lesson_booking_info.objects.get(id=1).booking_status)

        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'}
        response = \
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接下來測試學生的預扣時數是否有正確被扣除
        self.assertEqual(
            (
                10 * 60 - 140,  # 可用時數應該為原先購買的時數減掉 140 分鐘
                0,  # 預扣時數此時應該為 0 ，因為沒有其他的預約了
                140  # 已消耗的時數
            ),
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).available_remaining_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).withholding_minutes,
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                    student_auth_id = student_profile.objects.get(id=1).auth_id,
                    student_purchase_record_id = 1,  # 因為只購買過一次而已
                    lesson_id = 1
                ).confirmed_consumed_minutes
            ),
            student_remaining_minutes_of_each_purchased_lesson_set.objects.values()
        )


class REVIEWS_TESTS(TestCase):
    '''
    測試評論功能是否正常運作
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
            'regName': 'test_name_1',
            'regNickname': 'test_nickname_1',
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
        teacher_post_data['regName'] = 'test_name_2~~',
        teacher_post_data['regNickname'] = 'test_nickname_2~~',
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建了2個老師
        
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
            'userID': teacher_profile.objects.get(id=1).auth_id,   # 這是老師1的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test1111',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test11111',
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
            'userID': teacher_profile.objects.get(id=2).auth_id,   # 這是老師2的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test2222',
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

        self.available_date_11_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[10].date
        self.available_date_12_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[11].date
        self.available_date_13_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[12].date
        self.available_date_4_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[3].date
        self.available_date_15_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[14].date


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name1)
            shutil.rmtree('user_upload/students/' + self.test_student_name2)
            shutil.rmtree('user_upload/students/' + self.test_student_name3)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name1)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name2)
        except:
            pass

    
    def test_if_teacher_write_student_reviews_creates_record_and_update_student_profile(self):
        '''
        測試老師給學生的評價能否成功送出
        '''
        teacher_review_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'lesson_booking_info_id': 1,
            'score_given': 4,
            'remark_given': 'oh yayayayayayya',
            'is_student_late_for_lesson': 'false',
            'is_student_frivolous_in_lesson': 'false',
            'is_student_or_parents_not_friendly': 'true'
        }
        response = \
            self.client.post(path='/api/lesson/teacherWriteStudentReviews/', data=teacher_review_post_data)
        
        self.assertIn('failed', str(response.content, "utf8"))  # 因為沒有對應的預約跟完課紀錄

        # 來建立完整的資料
        # 先購買 老師1 的 10:90
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(10*800*.9),
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:0,1,2,3,4,5;'} 
            # 預約了180分鐘  00:00 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # print(f'inner info {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 0, 0)
        end_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 3, 0)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 這時候應該可以進行評價了，先嘗試老師評價學生

        remark_given = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
        teacher_review_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'lesson_booking_info_id': 1,
            'score_given': 7,
            'remark_given': remark_given,
            'is_student_late_for_lesson': '',
            'is_student_frivolous_in_lesson': 'false',
            'is_student_or_parents_not_friendly': 'true'
        }
        response = \
            self.client.post(path='/api/lesson/teacherWriteStudentReviews/', data=teacher_review_post_data)
        self.assertIn('success', str(response.content, "utf8"))  # 即使分數超過5分，也會變成5分

        # 測試有沒有產生一筆新紀錄
        self.assertEqual(1, student_reviews_from_teachers.objects.count(),
            student_reviews_from_teachers.objects.values())

        self.assertEqual(
            (
                5,
                remark_given,
                None,
                False,
                True
            ),
            (
                student_reviews_from_teachers.objects.get(id=1).score_given,
                student_reviews_from_teachers.objects.get(id=1).remark_given,
                student_reviews_from_teachers.objects.get(id=1).is_student_late_for_lesson,
                student_reviews_from_teachers.objects.get(id=1).is_student_frivolous_in_lesson,
                student_reviews_from_teachers.objects.get(id=1).is_student_or_parents_not_friendly
            ),
            student_reviews_from_teachers.objects.values()
        )
        
        # 確認學生的指數與上課時長是否正確
        self.assertEqual(
            (
                5,  # 平均得分,
                100.0,  # 認真比率
                0,  # 目前上課總時長應該是 0，因為狀態不是 "finished"
            ),
            (
                student_review_aggregated_info.objects.get(
                    student_auth_id=student_profile.objects.get(id=1).auth_id).get_score_given_to_times_mean(),
                student_review_aggregated_info.objects.get(
                    student_auth_id=student_profile.objects.get(id=1).auth_id).get_studious_index(),
                student_review_aggregated_info.objects.get(
                    student_auth_id=student_profile.objects.get(id=1).auth_id).receiving_review_lesson_minutes_sum,
            ),
            student_review_aggregated_info.objects.values())

        # 預約並完課第二門
        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2_t1}:4,5;'} 
            # 預約了60分鐘  02:00 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 2,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_2_t1.year, self.available_date_2_t1.month, self.available_date_2_t1.day, 2, 0)
        end_time = \
            datetime(self.available_date_2_t1.year, self.available_date_2_t1.month, self.available_date_2_t1.day, 3, 0)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 2,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)

        # 這裡先讓學生確認一下
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 2,
            'action': 'agree'}
        self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        
        # 進行評價
        teacher_review_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'lesson_booking_info_id': 2,
            'score_given': '',
            'remark_given': '',
            'is_student_late_for_lesson': 'true',
            'is_student_frivolous_in_lesson': '',
            'is_student_or_parents_not_friendly': ''
        }
        response = \
            self.client.post(path='/api/lesson/teacherWriteStudentReviews/', data=teacher_review_post_data)
        self.assertIn('success', str(response.content, "utf8")) 

        # 測試有沒有產生一筆新紀錄，總計2筆
        self.assertEqual(2, student_reviews_from_teachers.objects.count(),
            student_reviews_from_teachers.objects.values())

        self.assertEqual(
            (
                None,
                None,
                True,
                None,
                None
            ),
            (
                student_reviews_from_teachers.objects.get(id=2).score_given,
                student_reviews_from_teachers.objects.get(id=2).remark_given,
                student_reviews_from_teachers.objects.get(id=2).is_student_late_for_lesson,
                student_reviews_from_teachers.objects.get(id=2).is_student_frivolous_in_lesson,
                student_reviews_from_teachers.objects.get(id=2).is_student_or_parents_not_friendly
            ),          
            student_reviews_from_teachers.objects.values()
        )

        # 測試學生的個人評價整合檔有沒有更新紀錄
        # 此時student_review_aggregated_info應該有三筆資料(3個學生)
        self.assertEqual(3, student_review_aggregated_info.objects.count(),
            student_review_aggregated_info.objects.values())
            
        # 學生 1 應該有兩筆評價
        self.assertEqual(2, 
            student_review_aggregated_info.objects.get(student_auth_id=student_profile.objects.get(id=1).auth_id).reviewed_times,
            student_review_aggregated_info.objects.values())

        
        # 確認學生的指數與上課時長是否正確
        self.assertEqual(
            (
                2.5,  # 平均得分,
                50.0,  # 準時比率
                60,  # 目前上課總時長應該是60，因為狀態已經變成 "finished"
            ),
            (
                student_review_aggregated_info.objects.get(
                    student_auth_id=student_profile.objects.get(id=1).auth_id).get_score_given_to_times_mean(),
                student_review_aggregated_info.objects.get(
                    student_auth_id=student_profile.objects.get(id=1).auth_id).get_on_time_index(),
                student_review_aggregated_info.objects.get(
                    student_auth_id=student_profile.objects.get(id=1).auth_id).receiving_review_lesson_minutes_sum,
            ),
            student_review_aggregated_info.objects.values())

        # 接著讓學生確認第一門課
        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'}
        self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        s_a_id = student_profile.objects.get(id=1).auth_id
        # 確認時數是否變成 240 分鐘
        self.assertEqual(240, 
            student_review_aggregated_info.objects.get(
                    student_auth_id=student_profile.objects.get(id=1).auth_id).receiving_review_lesson_minutes_sum,
            f'{student_review_aggregated_info.objects.values().filter(student_auth_id=s_a_id)} \n\
                 {lesson_booking_info.objects.values().filter(student_auth_id=s_a_id)}')


        student_public_reviews_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id}
        response = \
            self.client.get(path='/api/account/getStudentPublicReview/', data=student_public_reviews_post_data)
        self.assertEqual(200, response.status_code)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"score_given_to_times_mean": 2.5', str(response.content, "utf8"))
        self.assertIn('"on_time_index": 50.0', str(response.content, "utf8"))
        self.assertIn('"studious_index": 100.0', str(response.content, "utf8"))
        self.assertIn('"friendly_index": 50.0', str(response.content, "utf8"))
        self.assertIn('"reviewed_times": 2', str(response.content, "utf8"))
        self.assertIn('"receiving_review_lesson_minutes_sum": 240', str(response.content, "utf8"))
        self.assertIn('"all_student_remarks": []', str(response.content, "utf8"))
        # self.fail(str(response.content, "utf8"))
        

    def test_if_student_writes_teacher_reviews_creates_record_and_update_teacher_profile(self):
        '''
        測試學生給老師的評價能否成功送出
        '''
        student_review_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lesson_booking_info_id': 1,
            'score_given': 4,
            'remark_given': 'oh yayayayayayya',
            'is_teacher_late_for_lesson': 'false',
            'is_teacher_frivolous_in_lesson': 'true',
            'is_teacher_incapable': 'false'
        }
        response = \
            self.client.post(path='/api/lesson/studentWriteTeacherReviews/', data=student_review_post_data)
        
        self.assertIn('failed', str(response.content, "utf8"))  # 因為沒有對應的預約跟完課紀錄

        # 來建立完整的資料
        # 先購買 老師1 的 10:90
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(10*800*.9),
            'q_discount': 0}
        response = \
            self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token': '',
            'type': '',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:0,1,2,3,4,5;'} 
            # 預約了180分鐘  00:00 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # print(f'inner info {student_remaining_minutes_of_each_purchased_lesson_set.objects.values()}')
        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 0, 0)
        end_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 3, 0)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        response = \
            self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 這時候應該可以進行評價了，嘗試學生評價老師

        remark_given = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
        student_review_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lesson_booking_info_id': 1,
            'score_given': 6,
            'remark_given': remark_given,
            'is_teacher_late_for_lesson': 'false',
            'is_teacher_frivolous_in_lesson': 'true',
            'is_teacher_incapable': 'false'
        }
        response = \
            self.client.post(path='/api/lesson/studentWriteTeacherReviews/', data=student_review_post_data)
        self.assertIn('success', str(response.content, "utf8"))  # 即使分數超過5分，也會變成5分

        # 測試有沒有產生一筆新紀錄
        self.assertEqual(1, lesson_reviews_from_students.objects.count(),
            lesson_reviews_from_students.objects.values())

        self.assertEqual(
            (
                5,
                remark_given,
                False,
                True,
                False
            ),
            (
                lesson_reviews_from_students.objects.get(id=1).score_given,
                lesson_reviews_from_students.objects.get(id=1).remark_given,
                lesson_reviews_from_students.objects.get(id=1).is_teacher_late_for_lesson,
                lesson_reviews_from_students.objects.get(id=1).is_teacher_frivolous_in_lesson,
                lesson_reviews_from_students.objects.get(id=1).is_teacher_incapable
            ),
            lesson_reviews_from_students.objects.values()
        )

        # teacher_review_aggregated_info 應該已經有老師對應的資料了
        self.assertEqual(1, teacher_review_aggregated_info.objects.filter(
            teacher_auth_id = teacher_profile.objects.get(id=1).auth_id
        ).count(),
            teacher_review_aggregated_info.objects.values())

        # 確認老師的指數與上課時長是否正確
        self.assertEqual(
            (
                5,  # 平均得分,
                100.0,  # 準時指數
                0,  # 認真指數
                100.0,  # 適任指數
                0,  # 目前上課總時長應該是 0，因為狀態不是 "finished"
            ),
            (
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).get_score_given_to_times_mean(),
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).get_on_time_index(),
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).get_diligent_index(),
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).get_competent_index(),
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).receiving_review_lesson_minutes_sum,
            ),
            teacher_review_aggregated_info.objects.values())

        # 預約並完課第二門
        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_2_t1}:4,5;'} 
            # 預約了60分鐘  02:00 - 03:00
        response = \
            self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 2,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_2_t1.year, self.available_date_2_t1.month, self.available_date_2_t1.day, 2, 0)
        end_time = \
            datetime(self.available_date_2_t1.year, self.available_date_2_t1.month, self.available_date_2_t1.day, 3, 0)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 2,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)

        # 這裡先讓學生確認一下第二門課
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 2,
            'action': 'agree'}
        self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        
        # 進行評價
        student_review_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lesson_booking_info_id': 2,
            'score_given': 2,
            'remark_given': 'this is a new remark.',
            'is_teacher_late_for_lesson': 'true',
            'is_teacher_frivolous_in_lesson': 'false',
            'is_teacher_incapable': 'false'
        }
        response = \
            self.client.post(path='/api/lesson/studentWriteTeacherReviews/', data=student_review_post_data)
        self.assertIn('success', str(response.content, "utf8"))  



        # 測試有沒有產生一筆新紀錄，總計2筆
        self.assertEqual(2, lesson_reviews_from_students.objects.count(),
            lesson_reviews_from_students.objects.values())

        self.assertEqual(
            (
                2,
                'this is a new remark.',
                True,
                False,
                False
            ),
            (
                lesson_reviews_from_students.objects.get(id=2).score_given,
                lesson_reviews_from_students.objects.get(id=2).remark_given,
                lesson_reviews_from_students.objects.get(id=2).is_teacher_late_for_lesson,
                lesson_reviews_from_students.objects.get(id=2).is_teacher_frivolous_in_lesson,
                lesson_reviews_from_students.objects.get(id=2).is_teacher_incapable
            ),          
            lesson_reviews_from_students.objects.values()
        )

        # 測試老師的個人評價整合檔有沒有更新紀錄
        # 此時teacher_review_aggregated_info應該有2筆資料(2個老師)
        self.assertEqual(2, teacher_review_aggregated_info.objects.count(),
            teacher_review_aggregated_info.objects.values())
            
        # 老師 1 應該有兩筆評價
        self.assertEqual(2, 
            teacher_review_aggregated_info.objects.get(teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).reviewed_times,
            teacher_review_aggregated_info.objects.values())

        
        # 確認老師的指數與上課時長是否正確
        self.assertEqual(
            (
                3.5,  # 平均得分,
                50.0,  # 準時指數
                50.0,  # 認真指數
                100.0,  # 適任指數
                60,  # 目前上課總時長應該是 60，因為第一門狀態不是 "finished"
            ),
            (
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).get_score_given_to_times_mean(),
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).get_on_time_index(),
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).get_diligent_index(),
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).get_competent_index(),
                teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).receiving_review_lesson_minutes_sum,
            ),
            teacher_review_aggregated_info.objects.values())

        # 接著讓學生確認第一門課
        # 此時，學生應該可以進行確認了
        confirmation_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'lesson_booking_info_id': 1,
            'action': 'agree'}
        response =\
            self.client.post(path='/api/lesson/lessonCompletedConfirmationFromStudent/', data=confirmation_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        
        t_a_id = teacher_profile.objects.get(id=1).auth_id
        # 確認時數是否變成 240 分鐘
        self.assertEqual(240, 
            teacher_review_aggregated_info.objects.get(
                    teacher_auth_id=teacher_profile.objects.get(id=1).auth_id).receiving_review_lesson_minutes_sum,
            f'{teacher_review_aggregated_info.objects.values().filter(teacher_auth_id=t_a_id)} \n\
                 {lesson_booking_info.objects.values().filter(teacher_auth_id=t_a_id)}')


        teacher_public_reviews_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id}
        response = \
            self.client.get(path='/api/account/getTeacherPublicReview/', data=teacher_public_reviews_post_data)
        self.assertEqual(200, response.status_code)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"score_given_to_times_mean": 3.5', str(response.content, "utf8"))
        self.assertIn('"on_time_index": 50.0', str(response.content, "utf8"))
        self.assertIn('"diligent_index": 50.0', str(response.content, "utf8"))
        self.assertIn('"competent_index": 100.0', str(response.content, "utf8"))
        self.assertIn('"reviewed_times": 2', str(response.content, "utf8"))
        self.assertIn('"receiving_review_lesson_minutes_sum": 240', str(response.content, "utf8"))
        self.assertIn('"all_teacher_remarks": []', str(response.content, "utf8"))
        # self.fail(str(response.content, "utf8"))


    def test_read_reviews_of_certain_lessons_exist(self):
        '''
        用來檢測「師生互看對方給予的評價」是否連線正常。
        '''
        read_reviews_post_data = {
            'lesson_booking_info_id': 1,
            'userID': student_profile.objects.get(id=1).auth_id,
            'type': 'student'
        }
        response = \
            self.client.post(path='/api/lesson/readReviewsOfCertainLessons/', data=read_reviews_post_data)
        self.assertEqual(200, response.status_code)


    def test_read_reviews_of_certain_lessons_work(self):
        '''
        用來檢測「師生互看對方給予的評價」是否運作正常。
        '''
        read_reviews_post_data = {
            'lesson_booking_info_id': 1,
            'userID': student_profile.objects.get(id=1).auth_id,
            'type': 'student'
        }
        response = \
            self.client.post(path='/api/lesson/readReviewsOfCertainLessons/', data=read_reviews_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertIn('"errCode": "1"', str(response.content, "utf8"))
        # 因為並不存在此門預約課程


        # 學生1 先購買 老師1 的 10:90
        purchased_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'teacherID': teacher_profile.objects.get(id=1).auth_id,
            'lessonID': lesson_info.objects.get(id=1).id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(10*800*.9),
            'q_discount': 0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchased_post_data)

        student_edit_booking_status_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,
            'token':'',
            'type':'',
            'purchase_recordID': student_purchase_record.objects.get(id=1).id,
            'status_update': 0, # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'}
        self.client.post(path='/api/account_finance/studentEditOrder/', data=student_edit_booking_status_post_data)
        # 此時，學生通知我們她已經完成付款
        purchase_obj = student_purchase_record.objects.get(id=1)
        purchase_obj.payment_status = 'paid'
        purchase_obj.save()
        # 我們確認她付款了

        # 接著讓學生進行預約
        booking_post_data = {
            'userID': student_profile.objects.get(id=1).auth_id,  # 學生的auth_id
            'lessonID': 1,
            'bookingDateTime': f'{self.available_date_1_t1}:0,1,2,3,4,5;'} 
            # 預約了180分鐘  00:00 - 03:00
        self.client.post(path='/api/lesson/bookingLessons/', data=booking_post_data)

        # 讓老師確認學生的預約
        change_booking_status_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'bookingID': 1,
            'bookingStatus': 'confirmed'}
        response = \
            self.client.post(path='/api/lesson/changingLessonBookingStatus/', data=change_booking_status_post_data)
        self.assertIn('success', str(response.content, "utf8"))

        # 接著老師進行完課
        start_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 0, 0)
        end_time = \
            datetime(self.available_date_1_t1.year, self.available_date_1_t1.month, self.available_date_1_t1.day, 3, 0)

        noti_post_data = {
                'userID': teacher_profile.objects.get(id=1).auth_id,
                'lesson_booking_info_id': 1,
                'lesson_date': str(self.available_date_1_t1),
                'start_time': start_time.strftime("%H:%M"),
                'end_time': end_time.strftime("%H:%M"),
                'time_interval_in_minutes': int((end_time - start_time).seconds / 60)
        }  # 測試看看這個 api 能不能產出對應的 record 來
        self.client.post(path='/api/lesson/lessonCompletedNotificationFromTeacher/', data=noti_post_data)
        # 這時候應該可以進行評價了，先查詢看看學生看評價
        student_read_reviews_post_data = {
            'lesson_booking_info_id': 1,
            'userID': student_profile.objects.get(id=1).auth_id,
            'type': 'student'
        }
        response = \
            self.client.post(path='/api/lesson/readReviewsOfCertainLessons/', data=student_read_reviews_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"score_given_to_teacher": -1', str(response.content, "utf8"))
        
        # 嘗試老師評價學生
        remark_1 = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
        teacher_review_post_data = {
            'userID': teacher_profile.objects.first().auth_id,
            'lesson_booking_info_id': 1,
            'score_given': 4,
            'remark_given': remark_1,
            'is_student_late_for_lesson': 'false',
            'is_student_frivolous_in_lesson': 'false',
            'is_student_or_parents_not_friendly': 'true'
        }
        self.client.post(path='/api/lesson/teacherWriteStudentReviews/', data=teacher_review_post_data)

        # 測試看看學生能不能看到老師留的評價
        student_read_reviews_post_data = {
            'lesson_booking_info_id': 1,
            'userID': student_profile.objects.get(id=1).auth_id,
            'type': 'student'
        }
        response = \
            self.client.post(path='/api/lesson/readReviewsOfCertainLessons/', data=student_read_reviews_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"score_given_to_student": 4', str(response.content, "utf8"))
        self.assertIn(f'"remark_given_to_student": "{remark_1}"', str(response.content, "utf8"))
        self.assertIn('"is_student_late_for_lesson": false', str(response.content, "utf8"))
        self.assertIn('"is_student_frivolous_in_lesson": false', str(response.content, "utf8"))
        self.assertIn('"is_student_or_parents_not_friendly": true', str(response.content, "utf8"))
        
        # 先查詢看看老師此時看評價，應該看不到學生給它的評價
        teacher_read_reviews_post_data = {
            'lesson_booking_info_id': 1,
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'
        }
        response = \
            self.client.post(path='/api/lesson/readReviewsOfCertainLessons/', data=teacher_read_reviews_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"score_given_to_student": 4', str(response.content, "utf8"))
        self.assertIn(f'"remark_given_to_student": "{remark_1}"', str(response.content, "utf8"))
        self.assertIn('"is_student_late_for_lesson": false', str(response.content, "utf8"))
        self.assertIn('"is_student_frivolous_in_lesson": false', str(response.content, "utf8"))
        self.assertIn('"is_student_or_parents_not_friendly": true', str(response.content, "utf8"))
        self.assertIn('"score_given_to_teacher": -1', str(response.content, "utf8"))
        self.assertIn(f'"remark_given_to_teacher": ""', str(response.content, "utf8"))
        self.assertIn('"is_teacher_late_for_lesson": null', str(response.content, "utf8"))
        self.assertIn('"is_teacher_frivolous_in_lesson": null', str(response.content, "utf8"))
        self.assertIn('"is_teacher_incapable": null', str(response.content, "utf8"))


        # 學生評價老師
        # 進行評價
        student_review_post_data = {
            'userID': student_profile.objects.first().auth_id,
            'lesson_booking_info_id': 1,
            'score_given': 3,
            'remark_given': 'this is a remark left by student.',
            'is_teacher_late_for_lesson': 'true',
            'is_teacher_frivolous_in_lesson': 'false',
            'is_teacher_incapable': 'false'
        }
        self.client.post(path='/api/lesson/studentWriteTeacherReviews/', data=student_review_post_data)

        # 老師再看一次
        teacher_read_reviews_post_data = {
            'lesson_booking_info_id': 1,
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'
        }
        response = \
            self.client.post(path='/api/lesson/readReviewsOfCertainLessons/', data=teacher_read_reviews_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"score_given_to_student": 4', str(response.content, "utf8"))
        self.assertIn(f'"remark_given_to_student": "{remark_1}"', str(response.content, "utf8"))
        self.assertIn('"is_student_late_for_lesson": false', str(response.content, "utf8"))
        self.assertIn('"is_student_frivolous_in_lesson": false', str(response.content, "utf8"))
        self.assertIn('"is_student_or_parents_not_friendly": true', str(response.content, "utf8"))
        self.assertIn('"score_given_to_teacher": 3', str(response.content, "utf8"))
        self.assertIn(f'"remark_given_to_teacher": "this is a remark left by student."', str(response.content, "utf8"))
        self.assertIn('"is_teacher_late_for_lesson": true', str(response.content, "utf8"))
        self.assertIn('"is_teacher_frivolous_in_lesson": false', str(response.content, "utf8"))
        self.assertIn('"is_teacher_incapable": false', str(response.content, "utf8"))

