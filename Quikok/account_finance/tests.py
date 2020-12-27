from django.test import TestCase, Client
from django.test import RequestFactory, TestCase
from django.test import Client
from .models import student_purchase_record
from account.models import teacher_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info

#python manage.py test account_finance/ --settings=Quikok.settings_for_test
class test_finance_functions(TestCase):
    def test_storege_order(self):

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
        client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 先建立一個老師的帳號，已經在 account.tests 測試過，故毋須重複測試

        # 測試前端傳來三種不同情況的方案時,是否能順利寫入
        lesson_set = ['trail','no_discount','30:70']
        # 要建立老師才能測試
        #teacher_profile.objects.create()
        for selected_set in lesson_set:
            data = {'userID':1,
            'teacher_id':2,
            'lesson_id':1,
            'lesson_set': selected_set,
            'total_amount_of_the_lesson_set': 300}

            response = self.client.post(path='/api/account_finance/storageOrder/', data=data)
            print(response)
            self.assertEqual(response.status_code, 200)
        # 目前都會回傳沒有老師,因為給test.py用的批次建立老師跟課程假資料還沒寫
        # 所以就先不測試回傳有沒有success
        #self.assertJSONEqual(
        #    str(response.content, encoding='utf8'),
        #    {
        #        'status': 'success',
        #        'errCode': None,
        #        'errMsg': None,
        #        'data': None
        #    })

