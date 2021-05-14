from account.models import student_profile, teacher_profile, general_available_time, user_token
from account.models import specific_available_time
from chatroom.models import chat_room
from django.contrib.auth.models import User
from itertools import product as pdt
import pandas as pd
import os, logging, re
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta

from lesson.models import lesson_card, lesson_info


logger_account = logging.getLogger('account_info')


def clean_files(folder_path, key_words):
    for each_file in os.listdir(folder_path):
        if key_words in each_file:
            os.unlink(os.path.join(folder_path, each_file))


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
        # 以下幾個不要直接改資料庫內容
        exclude_data_name = ['token','userID',"upload_snapshot"]
        student_auth_id = kwargs['userID']
        
        student_profile_object = self.check_if_student_exist(student_auth_id)
        if self.status == 'failed':
            return (self.status, self.errCode, self.errMsg, self.data)
        else:
            try:
                that_student = student_profile_object.first()
                student_profile_all_colname = [a.name for a in student_profile._meta.get_fields()]
                # 用student_profile裡的欄位名稱與前端傳來的名稱做交集
                intersection_data = [kwargs.keys() & student_profile_all_colname]
                username = that_student.username
                for colname in intersection_data[0]:
                    print(colname)
                    if colname not in exclude_data_name:
                        setattr(that_student, colname, kwargs[colname])

                if kwargs['upload_snapshot'] is not False:
                    snapshot = kwargs['upload_snapshot']
                    # 如果有收到user上傳的大頭貼資訊
                    print('收到學生大頭照: ', snapshot[0].name)
                    # 檢查路徑中是否原本已經有大頭照,有的話刪除舊圖檔
                    target_path = 'user_upload/students/' + username
                    clean_files(target_path, 'thumbnail')
                    fs = FileSystemStorage(location=target_path)
                    file_extension = snapshot[0].name.split('.')[-1]    
                    fs.save('thumbnail' + '.' + file_extension , snapshot[0]) # 檔名統一改成thumbnail開頭
                    setattr(
                        that_student,
                        'thumbnail_dir',
                        '/user_upload/students/' + username + '/thumbnail' + '.' + file_extension
                    )
                    self.data = dict()
                    self.data['upload_snapshot'] = 'thumbnail' + '.' + file_extension
                that_student.save()  # 等全設定完再儲存
                self.status = 'success'
                return (self.status, self.errCode, self.errMsg, self.data)
            except Exception as e:
                print(e)
                self.status = 'failed'
                self.errCode = '2'
                self.errMsg = 'Querying Data Failed.'
                return (self.status, self.errCode, self.errMsg, self.data)
    def create_student_group(self, **kwargs):
        pass
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

    def get_teacher_ids_who_have_lessons_on_sale(self):
        live_lesson_objects = lesson_info.objects.filter(selling_status='selling')
        return sorted(list(set(
            live_lesson_objects.values_list('teacher__auth_id', flat=True)
        )))

    def get_teacher_s_available_time(self, teacher_auth_ids):
        # 將老師們的空閒時間以下列方式呈現
        # {auth_id1: [time_list1],
        #   auth_id2: [time_list2]...}
        result = dict()
        try:
            len(teacher_auth_ids)
        except:
            teacher_auth_ids = [teacher_auth_ids,]
        for each_auth_id in teacher_auth_ids:
            time_query_set = \
                general_available_time.objects.filter(
                    teacher_model__auth_id=each_auth_id
                ).exclude(
                    time=''
                ).values_list('time', flat=True)
            # 'original time_query_set'
            #<QuerySet ['14,15,32,33,34,35', '', '', '', '', '', '']>
            sub_results = list()
            for each_element_set in time_query_set:
                for each_element in each_element_set.split(','):
                    #if each_element in ['47', 47]:
                    #    pass # 為了避免跨日問題,如果老師有開放時段47也不回傳
                    #else:
                    sub_results.append(eval(each_element))
            sub_results = list(set(sub_results))
            # print('sub_results', sub_results)
            result[each_auth_id] = sub_results
        return result

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

            general_available_time_to_return = ''
            specific_available_time_to_return = ''
            if general_available_time.objects.filter(teacher_model__auth_id=teacher_auth_id).count() > 0:
                # 代表有找到老師的時間，所以也會有 specific_available_time
                weeks = list(general_available_time.objects.values_list('week', flat=True).filter(teacher_model__auth_id=teacher_auth_id))
                times = list(general_available_time.objects.values_list('time', flat=True).filter(teacher_model__auth_id=teacher_auth_id))
                times_without47 = list()
                for time_num in times:
                    # 不回傳時段 47,所以拿掉.這邊有個可預見的bug,萬一有個week就只有47, 之後還 zip起來, 順序會亂掉
                    # 但若要處理這問題, 無論是先篩選出只有47時段的week,或是zip完再做都會改動到整個結構, 理論上只選47的機率是應該少之又少
                    # 在發生這件事之前或許已經把跨日解決了吧
                    _temp = time_num.replace(',47','')
                    times_without47.append(_temp)
                for w, t in zip(weeks, times_without47):
                    if len(t):
                        general_available_time_to_return += \
                            f'{w}:{t};'

                dates = list(specific_available_time.objects.values_list('date', flat=True).filter(teacher_model__auth_id=teacher_auth_id))
                times = list(specific_available_time.objects.values_list('time', flat=True).filter(teacher_model__auth_id=teacher_auth_id))

                for d, t in zip(dates, times):
                    if len(t):
                        specific_available_time_to_return += \
                            f'{d}:{t};'

            print('回傳給前端的一般時間:')
            print(general_available_time_to_return)
            print('回傳給前端的確切時間:')
            print(specific_available_time_to_return)
            print(specific_available_time.objects.values())

            _data['general_available_time'] = general_available_time_to_return
            _data['specific_available_time'] = specific_available_time_to_return

        
            self.status = 'success'
            self.data = _data
            return (self.status, self.errCode, self.errMsg, self.data)
        except Exception as e:
            print(f'return_teacher_profile_for_oneself_viewing {e}')
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
            print(f'查看老師資訊回傳:{self.data}')
            return (self.status, self.errCode, self.errMsg, self.data)
        except Exception as e:
            logger_account.error(f"return_teacher_profile_for_public_viewing {e}", exc_info=True)
            self.status = 'failed'
            self.errCode = '2'
            self.errMsg = 'Querying Data Failed.'
            return (self.status, self.errCode, self.errMsg, self.data)
    
    # 老師編輯個人資訊
    def edit_teacher_profile_tool(self, **kwargs):

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
                self.data = dict()
                teacher = teacher_profile_object.first()
                # 修改上課時間
                received_general_time = kwargs['teacher_general_availabale_time']
                print(received_general_time)
                temp_received_general_time_list = received_general_time.split(';')[0:-1] 
                # ['1:22','3:1,33';] split 之後最後一個會是空的所以去掉
                # 例外情況:傳來整串空的時候
                print(temp_received_general_time_list)
                # 尋找老師一般時間的資料
                general_time_queryset = teacher_profile_object.first().general_time.values()
                print(general_time_queryset)
                for received_week_and_time in temp_received_general_time_list : 
                    # 用week來比對是否老師有這個時段的資料
                    queryset_week_match = general_time_queryset.filter(week = received_week_and_time.split(':')[0])    
                    # 有,則這個時段已存在於db,則覆蓋
                    if len(queryset_week_match) > 0 : 
                        #week = received_week_and_time.split(':')[0] 
                        #time = received_week_and_time.split(':')[1]
                        #the_teacher_time_queryset = general_available_time.objects.filter(teacher_model= teacher.id).filter(week = week)
                        #the_teacher_time_queryset.update(time = time)
                        queryset_week_match.update(time = received_week_and_time.split(':')[1])
                        print('覆蓋原本時段')
                    else:
                        general_available_time.objects.create(
                            week = received_week_and_time.split(':')[0],
                            time = received_week_and_time.split(':')[1],
                            teacher_model = teacher
                        ).save()
                        print('新增時段')

                intersection_data = [kwargs.keys() & teacher_profile_all_colname] # is a dictionary
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
                    file_extentsion = snapshot[0].name.split('.')[-1]
                    fs.save('thumbnail'+'.'+ file_extentsion , snapshot[0]) # 檔名統一改成thumbnail開頭
                    thumbnail_dir = '/user_upload/teachers/' + username + '/' + 'thumbnail'+'.'+ file_extentsion
                    teacher_profile_object.update(thumbnail_dir = thumbnail_dir)
                    self.data['upload_snapshot'] = thumbnail_dir

                 # 未認證證書
                else:
                    print('沒收到更新大頭貼')
                if kwargs['upload_cer'] is not False :
                    upload_cer_list = kwargs["upload_cer"]
                    username = teacher.username
                    for each_file in upload_cer_list:
                        print('收到老師認證資料: ', each_file.name)
                        folder_where_are_uploaded_files_be ='user_upload/teachers/' + username + '/unaproved_cer'
                        fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
                        fs.save(each_file.name, each_file)  

                lesson_card_objects = lesson_card.objects.filter(teacher_auth_id=auth_id)
                print('current teacher nickname:', teacher.nickname)
                print('current teacher thumbnail_dir:', teacher.thumbnail_dir)
                teacher = teacher_profile.objects.filter(auth_id=auth_id).first()
                print('teacher2 thumbnail_dir:',teacher.thumbnail_dir)
                for each_lesson_card_object in lesson_card_objects:
                    setattr(each_lesson_card_object, 'teacher_nickname', teacher.nickname)
                    setattr(each_lesson_card_object, 'teacher_thumbnail_path', teacher.thumbnail_dir)
                    setattr(each_lesson_card_object, 'teacher_nickname', teacher.nickname)
                    setattr(each_lesson_card_object, 'education', teacher.education_1)
                    setattr(each_lesson_card_object, 'education_is_approved', teacher.education_approved)
                    setattr(each_lesson_card_object, 'working_experience', teacher.company)
                    setattr(each_lesson_card_object, 'working_experience_is_approved', teacher.work_approved)
                    each_lesson_card_object.save() 
                print("課程小卡更新成功")
                self.status = 'success'
                return (self.status, self.errCode, self.errMsg, self.data)
            except Exception as e:
                print(f'edit_teacher_profile_tool {e}')
                self.status = 'failed'
                self.errCode = '2'
                self.errMsg = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                return (self.status, self.errCode, self.errMsg, self.data)


class auth_manager_for_password:
    def __init__(self):
        self.status = None
        self.errCode = None
        self.errMsg = None
        self.data = None
        self.after_14days =None
        self.token = None
    def token_maker(self):
        self.after_14days = datetime.now() + timedelta(days = 14)
        self.token = make_password(str(self.after_14days))
        #return(self.after_14days, self.token) # 這個有必要寫嗎? 
# 忘記密碼 身分驗證
    def member_forgot_password(self, **kwargs):
        def response_to_frontend(check_result):
            if check_result == 1:
                self.status = 'success'
                self.data = dict()
                self.data['token'] = temporary_token                        
                self.data['userID'] = user_auth_id
            elif check_result == 2:
                self.status = 'failed'
                self.errCode = '2'
                self.errMsg = 'Birth Date or Mobile Unmatch'
            else:
                pass
        try:
            user_record = User.objects.filter(username = kwargs['userName'])
            # 假設有找到這個人, 接著要找他是老師還是學生並且拿他的生日以及手機來做確認
            if len(user_record) > 0:
                the_user_record = user_record.first()
                # 產生暫時性token供改密碼驗證
                self.token_maker()
                temporary_token = self.token
                user_auth_id = the_user_record.id
                find_teacher = teacher_profile.objects.filter(auth_id = user_auth_id)
                birth_date_unchecked = kwargs['userBirth']
                mobile_unchecked = kwargs['userMobile']
                
                if len(find_teacher) > 0:
                    birth_date_record = str(find_teacher.first().birth_date)
                    mobile_record = find_teacher.first().mobile
                    print(birth_date_record,mobile_record,birth_date_unchecked,mobile_unchecked)
                    if birth_date_record == birth_date_unchecked:
                        if mobile_record == mobile_unchecked:
                            user_token.objects.update_or_create(authID_object = user_record.first(), 
                                    defaults = {'logout_time' : self.after_14days,
                                                'token' : self.token
                                                },)
                            response_to_frontend(1)
                        else:
                            response_to_frontend(2)
                    else:
                        response_to_frontend(2)
                else:
                    user_is_student = student_profile.objects.filter(auth_id = user_auth_id).first()
                    birth_date_record = str(user_is_student.birth_date)
                    mobile_record = user_is_student.mobile
                    print(birth_date_record,mobile_record,birth_date_unchecked,mobile_unchecked)
                    if birth_date_record == birth_date_unchecked:
                        if mobile_record == mobile_unchecked:
                            check_result = 1
                            user_token.objects.update_or_create(authID_object = user_record.first(), 
                                                                defaults = {'logout_time' : self.after_14days,
                                                                            'token' : self.token
                                                                            },)
                            response_to_frontend(check_result)
                        else:
                            response_to_frontend(2)
                    else:
                        response_to_frontend(2)
            else:
                self.status = 'failed'
                self.errCode = '1'
                self.errMsg = 'Found No UserID'
        
        except Exception as e:
            print(e)
            self.status = 'failed'
            self.errCode = '3'
            self.errMsg = 'Querying Data Failed.'

        return (self.status, self.errCode, self.errMsg, self.data)
# 忘記密碼 身分驗證2 + 與重置密碼
    def member_reset_password(self, **kwargs):
        def response_to_frontend(check_result):
            if check_result == 1:
                self.status = 'failed'
                self.errCode = '1'
                self.errMsg = 'Token Unmatch'
        user_record = User.objects.filter(id = kwargs['userID'])
        if len(user_record) > 0:
            user_token_record = user_token.objects.filter(authID_object = user_record.first())
            if len(user_token_record) > 0:
                try:
                    print('資料庫裡的token: '+ user_token_record.first().token)
                    print('前端傳來的token: '+ str(kwargs['token']))
                    if user_token_record.first().token == kwargs['token']:
                        
                        user_record.update(password = kwargs['newUserPwd'])
                        self.status = 'success'
                        #self.data = dict()
                        #self.data['token'] = temporary_token                        
                        #self.data['userID'] = user_auth_id
                    else:
                        check_result = 1
                        response_to_frontend(check_result)
 
                except Exception as e:
                    print(e)
                    self.status = 'failed'
                    self.errCode = '2'
                    self.errMsg = 'Querying Data Failed.'
            else:
                check_result = 1
                response_to_frontend(check_result)
        else:
            self.status = 'failed'
            self.errCode = '0'
            self.errMsg = 'Found No UserID'


        
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


    



        
