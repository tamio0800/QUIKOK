from django.test import TestCase
from account.models import dev_db, student_profile, teacher_profile
import pandas as pd
import os

'''
-- SELECT * FROM quikok_db.account_dev_db;
use quikok_db;
insert into account_dev_db
	(
		username, password, name, birth_date, is_male, date_join
    )
values
	(
		"test_1", "00000000", "annie", "2009-10-04", 0, now()
        ""   
	)'''

class user_db_manager:
    def __init__(self):
        pass
    def create_user(self, **kwargs):

lesson_file = ""
lesson_df = pd.read.excel(lesson_file)


            student_profile.objects.create(
                username = username,
                password = password,
                balance = 0,
                withholding_balance = 0,
                name = name,
                nickname = nickname,
                birth_date = birth_date,
                is_male = is_male,
                intro = '',
                role = role,
                mobile = mobile,
                picture_folder = 'user_upload/'+ username,
                info_folder = 'user_upload/'+ username+ '/info_folder',
                update_someone_by_email = update_someone_by_email
            ).save()
            print('匯入課程成功')