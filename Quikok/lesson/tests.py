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
from account.models import teacher_profile
from django.contrib.auth.models import Permission, User, Group
from unittest import skip


# python manage.py test lesson/ --settings=Quikok.settings_for_test
class Lesson_Related_Functions_Test(TestCase):
 
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

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1
            }
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
        
        # 因為上方有 "試課優惠"，且也有 "單堂方案"，故應該有:
        #   trial、no_discount、10:90、20:80、30:75  這五種 sales_sets
        self.assertListEqual(
            ['trial', 'no_discount', '10:90', '20:80', '30:75'],
            all_lesson_1_sales_sets,
            lesson_sales_sets.objects.values()
        )
        


        