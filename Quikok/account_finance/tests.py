from django.test import TestCase, Client
from django.test import RequestFactory, TestCase
from django.test import Client

class test_finance_functions(TestCase):
    def test_storege_order(self):
        self.client = Client()
        lesson_set = ['trail','no_discount','30:70']
        for selected_set in lesson_set:
            data = {'userID':1,
            'teacher_id':2,
            'lesson_id':1,
            'lesson_set':,
            'total_amount_of_the_lesson_set':}
            self.client.post(path='/api/account_fi/signupTeacher/', data=data)
            self.assertEqual(
                os.path.isdir('user_upload/teachers/' + test_username),
                True
            )
