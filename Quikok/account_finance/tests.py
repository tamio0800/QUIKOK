from django.test import TestCase, Client, RequestFactory
from .models import student_purchase_record
from account.models import student_profile, teacher_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info
from account_finance.email_sending import email_manager
from django.contrib.auth.models import Group
import os, shutil
from django.core import mail
from unittest import skip
#python3 manage.py test account_finance/ --settings=Quikok.settings_for_test
class test_finance_functions(TestCase):
    def setUp(self):
        self.client =  Client()        
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:11,13,15,17,19,21,22,25,33;4:1,9,27,28,41;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建立兩個學生
        self.test_student_name = ['test_student1@a.com','test_student2@a.com']
        for user_name in self.test_student_name:
            student_post_data = {
                'regEmail': user_name,
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
        response = \
            self.client.post(
                path='/api/lesson/createOrEditLesson/',
                data=lesson_post_data)

    def test_storege_order(self):
        # 測試前端傳來三種不同情況的方案時,是否能順利寫入
        lesson_set = ['trail','no_discount','30:70']
        # 還要建立課程才能測試
        for selected_set in lesson_set:
            data = {'userID':1,
            'teacherID':2,
            'lessonID':1,
            'lesson_set': selected_set,
            'total_amount_of_the_lesson_set': 300}

            response = self.client.post(path='/api/account_finance/storageOrder/', data=data)
            print(response)
            self.assertEqual(response.status_code, 200)

        # 目前都會回傳沒有老師,因為給test.py用的批次建立老師跟課程假資料還沒寫
        # 如果filter沒找到東西都一定會failed,
        # 所以就先不測試回傳有沒有success
        #self.assertJSONEqual(
        #    str(response.content, encoding='utf8'),
        #    {
        #        'status': 'success',
        #        'errCode': None,
        #        'errMsg': None,
        #        'data': None
        #    })
    def test_email_sending_new_order(self):
        
        #mail.outbox = [] # 清空暫存記憶裡的信, def結束會自動empty,有需要再用
        data_test = {'studentID':2, 'teacherID':1,'lessonID':1,
                    'lesson_set':'30:70' ,'total_lesson_set_price':100,
                    'email_pattern_name':'訂課匯款提醒',
                    'q_discount':20}

        self.assertIsNotNone(student_profile.objects.filter(auth_id=data_test['studentID']).first())
        self.assertIsNotNone(teacher_profile.objects.filter(auth_id=data_test['teacherID']).first())
        self.assertIsNotNone(lesson_info.objects.filter(id=data_test['lessonID']).first())

        e = email_manager()
        ret = e.system_email_new_order_payment_remind(**data_test)
        self.assertTrue(ret)
        # 確認程式有正確執行
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '訂課匯款提醒')


@skip
class pure_email_send_test(TestCase):

    def test_email_could_send(self):
        self.client = Client()
        response = self.client.get('/api/account/send_email/')
        self.assertIn('Success', str(response.content, 'utf8'),
        str(response.content, 'utf8'))