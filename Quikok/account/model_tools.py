from account.models import dev_db, student_profile, teacher_profile
from django.contrib.auth.models import User
import pandas as pd

class user_db_manager:
    def __init__(self):
        pass
    def create_user(self, **kwargs):
        if kwargs['user_type'] == 'user':
            if student_profile.objects.filter(username=kwargs['username']).count() == 0:
                # 沒有重複的username
                nickname = kwargs['name'] if (kwargs['nickname'] is None or kwargs['nickname'] == '') else kwargs['nickname']
                student_profile(
                    username = kwargs['username'],
                    password = kwargs['password_hash'],
                    name = kwargs['name'],
                    nickname = kwargs['nickname'],
                    birth_date = kwargs['birth_date'],
                    is_male = kwargs['is_male'],
                    role = kwargs['role'],
                    mobile = kwargs['mobile'],
                    picture_folder = kwargs['picture_folder'],
                    update_someone_by_email = kwargs['update_someone_by_email'],
                ).save()
                print(kwargs['username'], 'has been created.')

                # 複寫到auth User中
                User(
                    username = kwargs['username'],
                    password = kwargs['password_hash'],
                    is_superuser = 0,
                    first_name = '',
                    last_name = '',
                    email = '',
                    is_staff = 0,
                    is_active = 1,
                ).save()
                return True
            else:
                return False
        elif kwargs['user_type'] == 'vendor':
            pass

    def dev_create_user(self, **kwargs):
        if kwargs['user_type'] == 'user':
            if dev_db.objects.filter(username=kwargs['username']).count() == 0:
                # 沒有重複的username
                dev_db(
                    username = kwargs['username'],
                    password = kwargs['password'],
                    name = kwargs['name'],
                    birth_date = kwargs['birth_date'],
                    is_male = kwargs['is_male'],
                ).save()
                print(kwargs['username'], 'has been created.')
                return True
            else:
                return False
        elif kwargs['user_type'] == 'vendor':
            pass
    
    def dev_import_vendor(self, **kwargs):
        _df_tobe_imported = kwargs['dataframe']
        try:
            for i in range(_df_tobe_imported.shape[0]):
                if teacher_profile.objects.filter(username=_df_tobe_imported.loc[i, '電子郵件地址']).count() == 0:
                    teacher_profile(
                        username = _df_tobe_imported.loc[i, '電子郵件地址'],
                        password = _df_tobe_imported.loc[i, 'password_hash'],
                        name = _df_tobe_imported.loc[i, '名字（本名）'],
                        nickname = _df_tobe_imported.loc[i, '暱稱'],
                        birth_date = '1900-01-01',
                        is_male = '0',
                        intro = '',
                        mobile = _df_tobe_imported.loc[i, '聯絡電話'],
                        picture_folder = 'to_be_deleted',
                        tutor_exp_in_years = 0.5,
                        student_type = '',
                        subject_type = '',
                        id_cert = '',
                        education_1 = _df_tobe_imported.loc[i, '最高學歷/科系/正在就讀請寫年級'],
                        education_2 = _df_tobe_imported.loc[i, '次高學歷/科系'],
                        education_3 = '',
                        education_cert_1 = '',
                        education_cert_2 = '',
                        education_cert_3 = '',
                        occupation = _df_tobe_imported.loc[i, '現任單位／職位'],
                        company = '',
                        occupation_cert = '',
                    ).save()

                if User.objects.filter(username=_df_tobe_imported.loc[i, '電子郵件地址']).count() == 0:
                    User(
                        username = _df_tobe_imported.loc[i, '電子郵件地址'],
                        password = _df_tobe_imported.loc[i, 'password_hash'],
                        is_superuser = 0,
                        first_name = '',
                        last_name = '',
                        email = '',
                        is_staff = 0,
                        is_active = 1,
                    ).save()
            return True
        except Exception as e:
            print(e)
            return False
        
