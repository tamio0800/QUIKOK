from account.models import dev_db, student_profile, teacher_profile
from chatroom.models import chat_room
from django.contrib.auth.models import User
from itertools import product as pdt
import pandas as pd
import os

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
                    nickname = nickname,
                    birth_date = kwargs['birth_date'],
                    is_male = kwargs['is_male'],
                    intro = '',
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

    
    def admin_import_user(self, **kwargs):
        _df_tobe_imported = kwargs['dataframe']
        _df_tobe_imported['暱稱'][pd.isnull(_df_tobe_imported['暱稱'])] = \
            _df_tobe_imported['姓名'][pd.isnull(_df_tobe_imported['暱稱'])]
        for each_col in _df_tobe_imported.columns:
            _df_tobe_imported[each_col] = _df_tobe_imported[each_col].apply(lambda x: '' if pd.isnull(x) else x)
        try:
            for i in range(_df_tobe_imported.shape[0]):
                picture_folder = _df_tobe_imported.loc[i, '帳號'].replace('@', 'at')
                if picture_folder not in os.listdir('user_upload'):
                    os.mkdir(os.path.join('user_upload', picture_folder))

                if _df_tobe_imported.loc[i, '類別'] == 't':
                    # 老師用戶
                    if teacher_profile.objects.filter(username=_df_tobe_imported.loc[i, '帳號']).count() == 0:
                        teacher_profile(
                            username = _df_tobe_imported.loc[i, '帳號'],
                            password = _df_tobe_imported.loc[i, 'password_hash'],
                            name = _df_tobe_imported.loc[i, '姓名'],
                            nickname = _df_tobe_imported.loc[i, '暱稱'],
                            birth_date = '1900-01-01',
                            is_male = '0',
                            intro = _df_tobe_imported.loc[i, '自我介紹'][:150],
                            mobile = '0912-345-678',
                            picture_folder = picture_folder,
                            tutor_exp_in_years = 0.5,
                            student_type = '',
                            subject_type = '',
                            id_cert = '',
                            education_1 = '',
                            education_2 = '',
                            education_3 = '',
                            education_cert_1 = _df_tobe_imported.loc[i, '老師亮點1'][:10],
                            education_cert_2 = _df_tobe_imported.loc[i, '老師亮點2'][:10],
                            education_cert_3 = _df_tobe_imported.loc[i, '老師亮點3'][:10],
                            occupation = '',
                            company = '',
                            occupation_cert = '',
                        ).save()
                elif _df_tobe_imported.loc[i, '類別'] == 's':
                    # 學生用戶
                    if student_profile.objects.filter(username=_df_tobe_imported.loc[i, '帳號']).count() == 0:
                        student_profile(
                            username = _df_tobe_imported.loc[i, '帳號'],
                            password = _df_tobe_imported.loc[i, 'password_hash'],
                            name = _df_tobe_imported.loc[i, '姓名'],
                            nickname = _df_tobe_imported.loc[i, '暱稱'],
                            birth_date = '1900-01-01',
                            is_male = '0',
                            intro = _df_tobe_imported.loc[i, '自我介紹'][:150],
                            role = 'myself',
                            mobile = '0912-345-678',
                            picture_folder = picture_folder,
                            update_someone_by_email = '',
                        ).save()
                if User.objects.filter(username=_df_tobe_imported.loc[i, '帳號']).count() == 0:
                    User(
                        username = _df_tobe_imported.loc[i, '帳號'],
                        password = _df_tobe_imported.loc[i, 'password_hash'],
                        is_superuser = 0,
                        first_name = '',
                        last_name = '',
                        email = '',
                        is_staff = 0,
                        is_active = 1,
                    ).save()
                    print(_df_tobe_imported.loc[i, '帳號'], 'has been created.')
                else:
                    print(_df_tobe_imported.loc[i, '帳號'], 'has been already in Quikok database.')

            return True
        except Exception as e:
            print(e)
            return False

    def admin_create_chatrooms(self):
        # 建立所有(學生&老師)對上(老師)的組合，但不包含自己對自己
        sp = list(student_profile.objects.all())
        tp = list(teacher_profile.objects.all())
        sp.extend(tp)
        # 擴展sp, 代表老師也有可能變成學生的身分，但還是要到teacher_profile中抓資料
        unique_pairs = [(i.username, j.username) for i, j in pdt(sp, tp) if i.username != j.username]
        del((sp, tp))  # 釋放一些記憶體空間
        # 接下來要尋找每一個對應的老師/學生在auth.User中的id為何
        for s_username, t_username in unique_pairs:
            student_id, teacher_id = \
                User.objects.get(username=s_username).id, User.objects.get(username=t_username).id
            
            # 接下來檢查這個pair有沒有存在於chat_room中，沒有的話就加上去
            if chat_room.objects.filter(
                student_id=student_id,
                teacher_id=teacher_id).count() == 0:
                # 不存在
                chat_room(
                    student_id=student_id,
                    teacher_id=teacher_id
                ).save()
                print('Chat_room Created:\nstudent: ' + s_username + \
                    '\nteacher: ' + t_username + '\n')
            

            









        
