import os
import shutil
import numpy as np
from django.contrib.auth.models import User
from account.models import student_profile, teacher_profile, general_available_time
from datetime import date as date_function
class batch_generator:
    def __init__(self):
        self.text = '臣亮言：先帝創業未半，而中道崩殂。今天下三分，益州疲弊，此誠危急存亡之秋也。然侍衛之臣，不懈於內；忠志之士，忘身於外者，蓋追先帝之殊遇，欲報之於陛下也。誠宜開張聖聽，以光先帝遺德，恢弘志士之氣；不宜妄自菲薄，引喻失義，以塞忠諫之路也。宮中府中，俱為一體，陟罰臧否，不宜異同。若有作姦犯科，及為忠善者，宜付有司，論其刑賞，以昭陛下平明之治，不宜篇私，使內外異法也。'
        self.text_in_list = [_ for _ in self.text]
        self.subjects = \
            ['英文', '中文', '國文', '漢語', '德文', '數學', '理化', '物理', '化學',
            '科學', '電子學', '統計', '地理', '歷史', '英語', '美術', '程式設計',
            '托福', '多益', '雅思', '肚皮舞', '史地', '平面設計', '行銷', '建築學',
            '流體力學', '量子力學', '茅山道術', '財務工程', '電機', 'TOEIC', 'TOFEL', 'IELTS']
        self.people_thumbnail_path = 'account/batched_creating/people_thumbnail'
        self.lesson_background_path = 'account/batched_creating/lesson_background'
    def get_text(self, num=150):
            return ''.join(list(np.random.choice(self.text_in_list, num, True)))
    def date_string_2_dateformat(self, target_string):
        if not target_string == False:
            try:
                # 將前端的 2000-01-01格式改為20000101
                nodash_str = target_string.replace('-','')
                if len(nodash_str) == 8 :
                    _year, _month, _day = int(nodash_str[:4]), int(nodash_str[4:6]), int(nodash_str[-2:])
                    return date_function(_year, _month, _day)
                else:
                    return False
            except Exception as e:
                print(e)
                return False
        else:
            return False
    def create_batch_student_users(self, how_many):
        print('StARt')
        for i in range(1, how_many):
            username = 's' + str(i).rjust(5, '0') + '@edony_test.com'
            name = 'test_student_' + str(i).rjust(5, '0')
            if np.random.rand() > 0.5:
                nickname = 'ts_' + str(i).rjust(5, '0')
            else:
                nickname = name
            _year = str(np.random.randint(1900, 2011))
            _month = str(np.random.randint(1, 13)).rjust(2, '0')
            _day = str(np.random.randint(1, 28)).rjust(2, '0')
            birth_date = self.date_string_2_dateformat(
                _year + '-' + _month + '-' + _day)
            is_male =  np.random.rand() > 0.5
            rnd_index = np.random.choice([_ for _ in range(6)])
            role = ['myself', 'father', 'mother', 'sister', 'brother', 'others'][rnd_index]
            mobile = '0900-000000'
            update_someone_by_email = ''
            password = '8B6FA01313CE51AFC09E610F819250DA501778AD363CBA4F9E312A6EC823D42A'
            # 此處的password已經經過前端加密，故無需再加密
            obj = student_profile.objects.filter(username=username).first()
            auth_obj = User.objects.filter(username=username).first()
            if obj is None and auth_obj is None:
                if not os.path.isdir('user_upload/students'):
                    os.mkdir(os.path.join('user_upload/students'))
                if os.path.isdir(os.path.join('user_upload/students', username)):
                    # 如果已經有了這個資料夾，就刪除裡面所有項目並且重建
                    shutil.rmtree(os.path.join('user_upload/students', username))
                    print('User Folder Already Existed >> Rebuild It.')
                os.mkdir(os.path.join('user_upload/students', username))
                os.mkdir(os.path.join('user_upload/students/'+ username, 'info_folder'))
                # 存到 user_upload 該使用者的資料夾
                #大頭照
                if np.random.rand() > 0.7:
                    pic_name, pic_ext = np.random.choice(os.listdir(self.people_thumbnail_path)).split('.')
                    thumbnail_dir = '/user_upload/students/' + username + '/' + 'thumbnail'+'.'+ pic_ext
                    shutil.copy(
                        os.path.join(self.people_thumbnail_path, pic_name + '.' + pic_ext),
                        thumbnail_dir[1:]
                    )
                else:
                    thumbnail_dir = ''
                user_created_object = \
                    User.objects.create(
                        username = username,
                        password = password,
                        is_superuser = 0,
                        first_name = '',
                        last_name = '',
                        email = '',
                        is_staff = 0,
                        is_active = 1,
                    )
                # 用create()的寫法是為了知道這個user在auth裡面的id為何
                user_created_object.save()
                print('auth建立')
                print('建立新學生資料')
                student_profile.objects.create(
                    auth_id = user_created_object.id,
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
                    user_folder = 'user_upload/'+ username,
                    info_folder = 'user_upload/'+ username+ '/info_folder',
                    thumbnail_dir = thumbnail_dir ,
                    update_someone_by_email = update_someone_by_email
                ).save()
                print('student_profile建立: ', username)
                # 回前端
            else:
                if obj is not None:
                    print('此帳號已註冊過學生類別!')
                elif auth_obj is not None:
                    print('此帳號已註冊到全站資料中!')
    def create_batch_teacher_users(self, how_many): 
        for i in range(0, how_many):
            username = 't' + str(i).rjust(5, '0') + '@edony_test.com'
            name = 'test_teacher_' + str(i).rjust(5, '0')
            if np.random.rand() > 0.5:
                nickname = 'tt_' + str(i).rjust(5, '0')
            else:
                nickname = name
            password = '8B6FA01313CE51AFC09E610F819250DA501778AD363CBA4F9E312A6EC823D42A'     
            _year = str(np.random.randint(1900, 2011))
            _month = str(np.random.randint(1, 13)).rjust(2, '0')
            _day = str(np.random.randint(1, 28)).rjust(2, '0')
            birth_date = self.date_string_2_dateformat(
                _year + '-' + _month + '-' + _day)
            is_male = np.random.rand() > 0.5
            intro = self.get_text(150)
            mobile = '0900-000999'
            tutor_experience = np.random.choice(['1年以內','1-3年','3-5年','5-10年','10年以上'])
            subject_type = ', '.join(list(np.random.choice(self.subjects, np.random.randint(1, 10))))
            education_1 = self.get_text(22) # 沒填的話前端傳空的過來
            education_2 = self.get_text(22)
            education_3 = self.get_text(22)
            company = self.get_text(22)
            special_exp = self.get_text(22)
            # 一般開課時間
            user_folder = username 
            print('收到老師註冊資料', username)
            # print('判斷收到老師資料是正常的')
            # 先檢查有沒有這個username存在，存在的話會return None給obj
            obj = teacher_profile.objects.filter(username=username).first()
            auth_obj = User.objects.filter(username=username).first()
            # 下面這個條件式>> 皆非(a為空 或是 b為空) >> a跟b都不能為空>> annie0918:應該是兩個都要空才對
            if obj is None and auth_obj is None :
                print('還沒註冊過,建立 teacher_profile')
                ### 長出老師相對應資料夾 
                # 目前要長的有:放一般圖檔的資料夾user_folder(大頭照、可能之後可放宣傳圖)、未認證的資料夾unaproved_cer、
                # 已認證過的證書aproved_cer、user_info 將來可能可以放考卷檔案夾之類的、課程統一資料夾lessons、 
                if not os.path.isdir('user_upload/teachers'):
                    os.mkdir(os.path.join('user_upload/teachers'))
                if os.path.isdir(os.path.join('user_upload/teachers', user_folder)):
                    # 如果已經有了這個資料夾，就刪除裡面所有項目並且重建
                    shutil.rmtree(os.path.join('user_upload/teachers', user_folder))
                    print('User Folder Already Existed >> Rebuild It.')
                os.mkdir(os.path.join('user_upload/teachers', user_folder))
                os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "unaproved_cer"))
                os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "aproved_cer"))
                os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "user_info")) # models裡的info_folder
                os.mkdir(os.path.join('user_upload/teachers/'+ user_folder, "lessons"))
                print('已幫老師建立5個資料夾')
                # for迴圈如果沒東西會是空的.  getlist()裡面是看前端的 multiple name
                if np.random.rand() > 0.5:
                    pic_path = self.people_thumbnail_path
                    pic_name, pic_ext = np.random.choice(os.listdir(pic_path)).split('.')
                    thumbnail_dir = '/user_upload/teachers/' + user_folder + '/' + 'thumbnail'+'.'+ pic_ext
                    shutil.copy(
                        os.path.join(pic_path, pic_name + '.' + pic_ext),
                        thumbnail_dir[1:]
                    )
                else:
                    thumbnail_dir = ''
                user_created_object = \
                    User.objects.create(
                        username = username,
                        password = password,
                        is_superuser = 0,
                        first_name = '',
                        last_name = '',
                        email = '',
                        is_staff = 0,
                        is_active = 1,
                    )
                user_created_object.save()
                print('老師成功建立 User.objects')
                teacher_profile.objects.create(
                        auth_id = user_created_object.id,
                        username = username,
                        password = password,
                        balance = 0,
                        unearned_balance = 0, # 帳戶預進帳金額，改成會計用語
                        withholding_balance = 0,
                        name = name,
                        nickname = nickname,
                        birth_date = birth_date,
                        is_male = is_male,
                        intro = intro,
                        mobile = mobile,
                        thumbnail_dir = thumbnail_dir,
                        user_folder = 'user_upload/'+ user_folder ,
                        info_folder = 'user_upload/'+ user_folder + '/user_info', 
                        tutor_experience = tutor_experience,
                        subject_type = subject_type,
                        education_1 = education_1,
                        education_2 = education_2,
                        education_3 = education_3 ,
                        cert_unapproved = 'user_upload/'+ user_folder + '/unaproved_cer',
                        cert_approved = 'user_upload/'+ user_folder + '/aproved_cer',
                        id_approved = 0,
                        education_approved = 0,
                        work_approved = 0,
                        other_approved = 0, #其他類別的認證勳章
                        #occupation = if_false_return_empty_else_do_nothing(occupation), 
                        company = company,
                        special_exp = special_exp
                ).save()
                print('成功建立 teacher_profile')
                ## 寫入一般時間table
                # 因為models設定general_available_time與 teacher_profile 
                # 的teacher_name有foreignkey的關係
                # 因此必須用teacher_profile.objects 來建立這邊的teacher_name
                # (否則無法建立)
                teacher_object = teacher_profile.objects.get(username=username)
                for every_week in range(7):
                    temp_time = ','.join([ str(_) for _ in sorted(np.random.randint(0, 48, np.random.randint(0, 48, 1)))])
                    if len(temp_time) > 0:
                        general_available_time.objects.create(
                            teacher_model = teacher_object,
                            week = every_week,
                            time = temp_time
                                        ).save()
                print('老師成功建立 一般時間')



if __name__ == '__main__':
    the_bg = batch_generator()
    the_bg.create_batch_student_users(50)
    the_bg.create_batch_teacher_users(50)


