from account.models import dev_db, student_profile, teacher_profile, general_available_time
from chatroom.models import chat_room
from django.contrib.auth.models import User
from itertools import product as pdt
import pandas as pd
import os, re
from django.core.files.storage import FileSystemStorage
class student_manager:
    def __init__(self):
        self.status = None
        self.errCode = None
        self.errMsg = None
        self.data = None
    def check_if_student_exist(self, student_auth_id):
        student_profile_object = student_profile.objects.filter(auth_id=student_auth_id)
        if student_profile_object.first() is None:
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Found No Student.'
        else:
            return(student_profile_object)
    def return_student_profile_for_oneself_viewing(self, student_auth_id):
        # 顯示學生隱私資料for學生編輯個人資料
        student_profile_object = self.check_if_student_exist(student_auth_id)
        if self.status == 'failed':
            return (self.status, self.errCode, self.errMsg, self.data)
        else:
            try:
                _data = dict() 
                exclude_columns = [
                    'id','auth_id',  'info_folder',
                    'password', 'user_folder', 'date_join']
                for each_key, each_value in student_profile_object.values()[0].items():
                    if each_key not in exclude_columns:
                        _data[each_key] = each_value 
         
                self.status = 'success'
                self.data = _data
                return (self.status, self.errCode, self.errMsg, self.data)
            except Exception as e:
                print(e)
                self.status = 'failed'
                self.errCode = '2'
                self.errMsg = 'Querying Data Failed.'
                return (self.status, self.errCode, self.errMsg, self.data)
        
            
    def update_student_profile(self, **kwargs):
        # 學生資料編輯 只是方便對照
        _recevived_data_name = ['token','userID','mobile','nickname','update_someone_by_email',
        "upload_snapshot", 'intro']
        # 以下幾個不要直接改資料庫內容
        exclude_data_name = ['token','userID',"upload_snapshot"]
        #for a in kwargs.items():
        #    print(a)
        student_auth_id = kwargs['userID']
        student_profile_object = self.check_if_student_exist(student_auth_id)
        if self.status == 'failed':
            return (self.status, self.errCode, self.errMsg, self.data)
        else:
            try:
                student_profile = student_profile_object.first()
                username = student_profile.username
                for k, v in kwargs.items():
                    if k not in exclude_data_name:
                        setattr(student_profile, k, v)
                student_profile.save()
                if kwargs['upload_snapshot'] is not False :
                    snapshot = kwargs['upload_snapshot']
                    # 檢查路徑中是否原本已經有大頭照,有的話刪除舊圖檔
                    file_list = os.listdir('user_upload/students/' + username)
                    for file_name in file_list:
                        if re.findall('thumbnail.*', file_name):
                            os.unlink('user_upload/students/' + username +'/'+ file_name)

                    print('收到學生大頭照: ', snapshot[0].name)
                    folder_where_are_uploaded_files_be ='user_upload/students/' + username
                    fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
                    file_exten = snapshot[0].name.split('.')[-1]
                    fs.save('thumbnail'+'.'+ file_exten , snapshot[0]) # 檔名統一改成thumbnail開頭
                    thumbnail_dir = '/user_upload/students/' + username + '/' + 'thumbnail'+'.'+ file_exten
                    student_profile_object.update(thumbnail_dir = thumbnail_dir)

                self.status = 'success'
                return (self.status, self.errCode, self.errMsg, self.data)
            except Exception as e:
                print(e)
                self.status = 'failed'
                self.errCode = '2'
                self.errMsg = 'Querying Data Failed.'
                return (self.status, self.errCode, self.errMsg, self.data)
class teacher_manager:
    def __init__(self):
        self.status = None
        self.errCode = None
        self.errMsg = None
        self.data = None
    def check_if_teacher_exist(self, auth_id):
        teacher_profile_object = teacher_profile.objects.filter(auth_id=auth_id)
        if teacher_profile_object.first() is None:
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Found No teacher.'
        else:
            return(teacher_profile_object)
    #  老師個人資訊編輯頁(自己看自己)
    #  特定時間第一版先不做 10/27
    def return_teacher_profile_for_oneself_viewing(self, teacher_auth_id):
        # 老師編輯個人資料
        teacher_profile_object = teacher_profile.objects.filter(auth_id=teacher_auth_id)

        if teacher_profile_object.first() is None:
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Found No Teacher.'
            return (self.status, self.errCode, self.errMsg, self.data)
        try:
            _data = dict()
            # 不需要看到的欄位
            exclude_columns = [
                'teaching_history', 'id', 'teacher_of_the_lesson_snapshot',
                'teacher_of_the_lesson', 'password', 'user_folder', 'info_folder',
                'cert_unapproved', 'date_join', 'auth_id', 'cert_approved']
            for each_key, each_value in teacher_profile_object.values()[0].items():
                if each_key not in exclude_columns:
                    _data[each_key] = each_value
            # 一般時間
            general_available_time_object_records = \
                general_available_time.objects.filter(teacher_model__auth_id=teacher_auth_id).values()
            if len(general_available_time_object_records) > 0:
                # 代表有找到老師的時間
                general_available_time_list = list()
                for each_record in general_available_time_object_records:
                    general_available_time_list.append(
                        each_record['week'] + ':' + each_record['time']
                        )
                general_available_time_list = ';'.join(general_available_time_list)

            else:
                general_available_time_list = ''
            _data['general_available_time'] = general_available_time_list
            # 特定時間 第一版不做
            specific_available_time_list = list()
            specific_time_queryset = teacher_profile_object.first().specific_time.values()
            if len(specific_time_queryset) > 0: # 表示有特定時間
                for each_record in specific_time_queryset:
                    _date = each_record['date']
                    _time = each_record['time']
                    specific_available_time_list.append(_date + ':' + _time)
                specific_available_time_list = ';'.join(specific_available_time_list)
                _data['specific_available_time'] = specific_available_time_list
            else:
                pass # 應該不需要做甚麼事情

            self.status = 'success'
            self.data = _data
            return (self.status, self.errCode, self.errMsg, self.data)
        except Exception as e:
            print(e)
            self.status = 'failed'
            self.errCode = '2'
            self.errMsg = 'Querying Data Failed.'
            return (self.status, self.errCode, self.errMsg, self.data)
    #老師個人資訊公開頁
    def return_teacher_profile_for_public_viewing(self, teacher_auth_id):
        teacher_profile_object = teacher_profile.objects.filter(auth_id=teacher_auth_id)
        if teacher_profile_object.first() is None:
            self.status = 'failed'
            self.errCode = '1'
            self.errMsg = 'Found No Teacher.'
            return (self.status, self.errCode, self.errMsg, self.data)
        try:
            _data = dict()
            exclude_columns = [
                'auth_id','username','password','balance', 'withholding_balance',
                'teaching_history', 'id', 
                'teacher_of_the_lesson_snapshot',
                'teacher_of_the_lesson',  'user_folder', 'info_folder',
                'cert_unapproved', 'date_join',  'cert_approved']
            
            for each_key, each_value in teacher_profile_object.values()[0].items():
                if each_key not in exclude_columns:
                    _data[each_key] = each_value 
            
            self.status = 'success'
            self.data = _data
            return (self.status, self.errCode, self.errMsg, self.data)
        except Exception as e:
            print(e)
            self.status = 'failed'
            self.errCode = '2'
            self.errMsg = 'Querying Data Failed.'
            return (self.status, self.errCode, self.errMsg, self.data)
    
    # 老師編輯個人資訊
    def update_teacher_profile(self, **kwargs):
        teacher_profile_all_colname = [a.name for a in teacher_profile._meta.get_fields()] 
        # 以下幾個不要直接改資料庫內容
        exclude_data_name = ['token','userID',"upload_snapshot", "upload_cer"]
        #for a in kwargs.items():
        #    print(a)
        auth_id = kwargs['userID']
        teacher_profile_object = self.check_if_teacher_exist(auth_id)
        if self.status == 'failed':
            return (self.status, self.errCode, self.errMsg, self.data)
        else:
            try:
                teacher = teacher_profile_object.first()
                # 前端給的資料與資料庫colname交集
                intersection_data = [kwargs.keys() & teacher_profile_all_colname]
                print(intersection_data)
                for colname in intersection_data[0]:
                    if colname not in exclude_data_name:
                        setattr(teacher, colname, kwargs[colname])
                teacher.save()

                if kwargs['upload_snapshot'] is not False :
                    snapshot = kwargs['upload_snapshot']
                    username = teacher.username
                    # 檢查路徑中是否原本已經有大頭照,有的話刪除舊圖檔
                    file_list = os.listdir('user_upload/teachers/' + username)
                    for file_name in file_list:
                        if re.findall('thumbnail.*', file_name):
                            os.unlink('user_upload/teachers/' + username +'/'+ file_name)

                    print('老師更新大頭照: ', snapshot[0].name)
                    folder_where_are_uploaded_files_be ='user_upload/teachers/' + username
                    fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
                    file_exten = snapshot[0].name.split('.')[-1]
                    fs.save('thumbnail'+'.'+ file_exten , snapshot[0]) # 檔名統一改成thumbnail開頭
                    thumbnail_dir = '/user_upload/teachers/' + username + '/' + 'thumbnail'+'.'+ file_exten
                    teacher_profile_object.update(thumbnail_dir = thumbnail_dir)

                 # 未認證證書
                if kwargs['upload_cer'] is not False :
                    upload_cer_list = kwargs["upload_cer"]
                    username = teacher.username
                    
                    for each_file in upload_cer_list:
                        print('收到老師認證資料: ', each_file.name)
                        folder_where_are_uploaded_files_be ='user_upload/teachers/' + username + '/unaproved_cer'
                        fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
                        fs.save(each_file.name, each_file)    
    
                self.status = 'success'
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


    



        
