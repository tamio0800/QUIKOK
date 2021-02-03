import unittest
from time import time
from lesson.email_sending import email_manager

class EMAIL_TEST(unittest.TestCase):

    def setUp(self):
        self.M = email_manager()
        self.start_time = time()

    def test_how_long_does_it_take_to_send_an_email(self):
        self.M.send_teacher_when_student_buy_his_lesson(
            teacher_authID = 1, 
            student_authID=7, 
            lesson_title='t', 
            lesson_set='trial',
            price = 122 )