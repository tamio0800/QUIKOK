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
        print(str(response.content, encoding='utf8'))
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
            }
        )

    '''def test_before_signing_up_create_or_edit_a_lesson_exist(self):
        # 確認有找到這個views function
        self.factory = RequestFactory()
        request = self.factory.post('api/lesson/beforeSigningUpCreateOrEditLesson/')
        print(str(request))

    def test_get_lesson_cards_for_common_users_exist(self):
        # self.factory = RequestFactory()
        data = {
            'qty': 10,
            'filtered_by': None,
            'keywords': None,
            'ordered_by': None,
            'user_auth_id': 4,
            'only_show_ones_favorites': False
        }
        response = self.client.post(
            path='api/lesson/getLessonCardsForCommonUsers/',
            data=data,
            content_type='application/json',
        )
        print(str(response))'''
        