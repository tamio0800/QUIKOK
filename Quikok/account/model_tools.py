from account.models import dev_db, student_profile, teacher_profile, general_available_time
from chatroom.models import chat_room
from django.contrib.auth.models import User
from itertools import product as pdt
import pandas as pd
import os


class teacher_manager:
    def __init__(self):
        self.status = None
        self.errCode = None
        self.errMsg = None
        self.data = None

    def return_teacher_profile_for_oneself_viewing(self, teacher_auth_id):
        teacher_profile_object = teacher_profile.objects.filter(auth_id=teacher_auth_id)
        if teacher_profile_object.first() is None:
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Found No Teacher.'
            return (self.status, self.errCode, self.errMsg, self.data)
        try:
            _data = dict()
            exclude_columns = [
                'specific_time', 'teaching_history', 'id', 'teacher_of_the_lesson_snapshot',
                'teacher_of_the_lesson', 'password', 'user_folder', 'info_folder',
                'cert_unapproved', 'date_join', 'auth_id', 'cert_approved']
            for each_key, each_value in teacher_profile_object.values()[0].items():
                if each_key not in exclude_columns:
                    _data[each_key] = each_value 
            general_available_time_object_records = \
                general_available_time.objects.filter(teacher_model__auth_id=teacher_auth_id).values()
            print("XXXXXXXXXXXXXXXX")
            if len(general_available_time_object_records) > 0:
                # 代表有找到老師的時間
                general_available_time = list()
                for each_record in general_available_time_object_records:
                    general_available_time.append(
                        each_record['week'] + ':' + each_record['time']
                        )
                general_available_time = ';'.join(general_available_time)
            else:
                general_available_time = ''
            _data['general_available_time'] = general_available_time
            self.status = 'success'
            self.data = _data
            return (self.status, self.errCode, self.errMsg, self.data)
        except Exception as e:
            print(e)
            self.status = 'failed'
            self.errCode = '2'
            self.errMsg = 'Querying Data Failed.'
            return (self.status, self.errCode, self.errMsg, self.data)

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

    # 建立user 存放自己上傳檔案的資料夾
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
                            balance = _df_tobe_imported.loc[i, '帳戶餘額'], #餘額
                            unearned_balance = _df_tobe_imported.loc[i, '預扣'], # 預扣
                            withholding_balance = _df_tobe_imported.loc[i, '預進帳'], #預進帳
                            user_folder = 'user_upload/'+ _df_tobe_imported.loc[i, '帳號'] ,
                            info_folder = 'user_upload/'+ _df_tobe_imported.loc[i, '帳號'] +'/user_info', #尚未建立此資料夾
                            tutor_experience = _df_tobe_imported.loc[i, '教學年資'],
                            subject_type = _df_tobe_imported.loc[i, '科目與對象'],
                            education_1 = _df_tobe_imported.loc[i, '第一學歷'],
                            education_2 = _df_tobe_imported.loc[i, '第二學歷'],
                            education_3 = _df_tobe_imported.loc[i, '第三學歷'],
                            cert_unapproved = 'user_upload/'+ _df_tobe_imported.loc[i, '帳號'] + '/unaproved_cer',
                            cert_approved = 'user_upload/'+ _df_tobe_imported.loc[i, '帳號'] + '/aproved_cer',
                            id_approved = 0,
                            education_approved = 0,
                            work_approved = 0,
                            other_approved = 0, #其他類別的認證勳章 
                            company = _df_tobe_imported.loc[i, '任職公司']
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

if __name__ == '__main__':
    from shutil import copy2
    teacher_icon = 'assets/IMG/snapshotA.png'
    student_icon = 'assets/IMG/snapshotB.png'

    for each_folder in os.listdir('user_upload'):
        if each_folder[0] == 's':
            copy2(student_icon, os.path.join('user_upload', each_folder, 'snapshot.png'))
        else:
            copy2(teacher_icon, os.path.join('user_upload', each_folder, 'snapshot.png'))


    



        
