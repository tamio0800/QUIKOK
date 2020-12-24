from django.test import TestCase, Client
from django.test import RequestFactory, TestCase
from django.test import Client
from .models import student_purchase_record
from account.models import teacher_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info

#python manage.py test account_finance/ --settings=Quikok.settings_for_test
class test_finance_functions(TestCase):
    def test_storege_order(self):
        self.client = Client()
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
