from django.test import RequestFactory, TestCase
from django.test import Client
import pandas as pd
import os
from lesson import lesson_tools

class Lesson_Related_Functions_Test(TestCase):

    def test_before_signing_up_create_or_edit_a_lesson_exist(self):
        # 測試這個函式是否存在，並且應該回傳status='success', errCode=None, errMsg=None
        # self.factory = RequestFactory()
        self.client = Client()
        response = self.client.post(path='/api/lesson/beforeSigningUpCreateOrEditLesson/')
        self.assertEqual(response.status_code, 200)
        

    def test_before_signing_up_create_or_edit_a_lesson_received_argument(self):
        # 測試這個函式能不能接受到自訂的「dummy_user_id」參數
        self.client = Client()
        response = self.client.post(
            path='/api/lesson/beforeSigningUpCreateOrEditLesson/',
            data={'dummy_user_id': 'tamio080011111'})
        print(str(response.content, encoding='utf8'))
        
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
            }
        )

    

        