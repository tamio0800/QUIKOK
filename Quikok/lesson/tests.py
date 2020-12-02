from django.test import RequestFactory, TestCase 
import pandas as pd
import os


class Lesson_Related_Functions_Test(TestCase):

    def test_create_or_edit_a_lesson_function_exist(self):
        self.factory = RequestFactory()
        request = self.factory.get('api/lesson/beforeSigningUpCreateOrEditLesson/')
        
        
        print(str(request))
