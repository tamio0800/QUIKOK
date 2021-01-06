from django.test import TestCase, Client, RequestFactory
from .models import student_purchase_record, student_remaining_minutes_of_each_purchased_lesson_set
from account.models import student_profile, teacher_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info
from account_finance.email_sending import email_manager
from django.contrib.auth.models import Group
import os, shutil
from django.core import mail
from unittest import skip
#python3 manage.py test account_finance/ --settings=Quikok.settings_for_test
class test_finance_functions(TestCase):
    def setUp(self):
        self.client =  Client()        
        Group.objects.bulk_create(
            [
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ]
        )
        self.test_username = 'test_teacher_user@test.com'
        teacher_post_data = {
            'regEmail': self.test_username,
            'regPwd': '00000000',
            'regName': 'test_name',
            'regNickname': 'test_nickname',
            'regBirth': '2000-01-01',
            'regGender': '0',
            'intro': 'test_intro',
            'regMobile': '0912-345678',
            'tutor_experience': '一年以下',
            'subject_type': 'test_subject',
            'education_1': 'education_1_test',
            'education_2': 'education_2_test',
            'education_3': 'education_3_test',
            'company': 'test_company',
            'special_exp': 'test_special_exp',
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:11,13,15,17,19,21,22,25,33;4:1,9,27,28,41;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建立兩個學生
        self.test_student_name = ['test_student1@a.com','test_student2@a.com']
        for user_name in self.test_student_name:
            student_post_data = {
                'regEmail': user_name,
                'regPwd': '00000000',
                'regName': 'test_student_name',
                'regBirth': '1990-12-25',
                'regGender': 1,
                'regRole': 'oneself',
                'regMobile': '0900-111111',
                'regNotifiemail': ''
            }
            self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        # 建立課程
        lesson_post_data = {
            'userID': 1,   # 這是老師的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 800,
            'discount_price': '10:90;20:80;30:75;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': 69,
            'highlight_1': 'test',
            'highlight_2': 'test',
            'highlight_3': 'test',
            'lesson_intro': 'test',
            'how_does_lesson_go': 'test',
            'target_students': 'test',
            'lesson_remarks': 'test',
            'syllabus': 'test',
            'lesson_attributes': 'test'      
            }
        self.lesson_post_data = lesson_post_data
        response = \
            self.client.post(
                path='/api/lesson/createOrEditLesson/',
                data=lesson_post_data)

    def test_storege_order(self):
        # 測試前端傳來三種不同情況的方案時,是否能順利寫入
        lesson_set = ['trial']#,'no_discount','30:70']
        # 還要建立課程才能測試
        for selected_set in lesson_set:
            data = {'userID':2,
            'teacherID':1,
            'lessonID':1,
            'sales_set': selected_set,
            'total_amount_of_the_sales_set': 300,
            'q_discount':0}

            response = self.client.post(path='/api/account_finance/storageOrder/', data=data)
            #print(response)
            self.assertEqual(response.status_code, 200)

        # 目前都會回傳沒有老師,因為給test.py用的批次建立老師跟課程假資料還沒寫
        # 如果filter沒找到東西都一定會failed,
        # 所以就先不測試回傳有沒有success
            self.assertJSONEqual(
                str(response.content, encoding='utf8'),
                {
                    'status': 'success',
                    'errCode': None,
                    'errMsg': None,
                    'data': 1 # 建立1號訂單
                })


    def test_if_storege_order_select_active_lesson_sales_set(self):
        '''
        這個測試用來確認，當老師修改課程內容後，購買的方案是不是真正要的那個方案
        '''
        # 嘗試更新課程
        self.lesson_post_data['action'] = 'editLesson'
        self.lesson_post_data['lessonID'] = 1  # 因為是課程編輯，所以需要給課程的id
        self.lesson_post_data['little_title'] = '新的圖片小標題'
        self.lesson_post_data['lesson_title'] = '新的課程標題'
        self.lesson_post_data['price_per_hour'] = 1230
        self.lesson_post_data['trial_class_price'] = -999  # 不試教了
        self.lesson_post_data['discount_price'] = '5:95;10:90;50:70;'
        
        response = self.client.post(path='/api/lesson/createOrEditLesson/', data=self.lesson_post_data)
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))
        # 確認課程更新成功
        
        lesson_set = '10:90'
        post_data = {
            'userID':2,
            'teacherID':1,
            'lessonID':1,
            'sales_set': lesson_set,
            'total_amount_of_the_sales_set': int(self.lesson_post_data['price_per_hour'] * 10 * 0.9),
            'q_discount':0
        }
        response = self.client.post(path='/api/account_finance/storageOrder/', data=post_data)
        self.assertIn('success', str(response.content, 'utf8'), str(response.content, 'utf8'))
        # 確認狀態成功
        # 確認DB總共有幾個課, sets及訂單數量
        self.assertEqual(lesson_info.objects.count(),1)
        #self.assertEqual(lesson_sales_sets.objects.count()),9) 更新set之後變成9種
        print(lesson_sales_sets.objects.all())
        self.assertEqual(student_purchase_record.objects.count(),1)
        # 接下來要確認抓到的 sales_set 是不是真正要的那個
        self.assertEqual(
            student_purchase_record.objects.filter(id=1).first().lesson_set_id,
            lesson_sales_sets.objects.filter(
                sales_set='10:90',
                total_amount_of_the_sales_set=int(self.lesson_post_data['price_per_hour'] * 10 * 0.9)
            ).first().id,
            lesson_sales_sets.objects.values()
        )

    
    def test_if_student_remaining_time_table_updated_after_unpaid_turned_into_paid_common_set(self):
        '''
        這個函式用來測試，當學生付完款(一般的方案)後，管理員或程式把該筆訂單的付款狀態設定為「已付款」後，
        學生的 student_remaining_minutes_of_each_purchased_lesson_set table 有沒有長出對應的資料。
        '''
        lesson_set = '10:90'
        post_data = {
            'userID':2,
            'teacherID':1,
            'lessonID':1,
            'sales_set': lesson_set,
            'total_amount_of_the_sales_set': int(self.lesson_post_data['price_per_hour'] * 10 * 0.9),
            'q_discount':0
        }  #先測試 10:90 看看是否成功
        self.client.post(path='/api/account_finance/storageOrder/', data=post_data)

        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,
            'unpaid',
            student_purchase_record.objects.values()
        )  # 目前應該是未付款的狀態

        # 如果我們將它設定為已付款，理論上應該會連動更新學生的 student_remaining_minutes_of_each_purchased_lesson_set
        the_student_purchase_record_object = \
            student_purchase_record.objects.get(id=1)
        the_student_purchase_record_object.payment_status = 'paid'
        the_student_purchase_record_object.save()

        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,
            'paid',
            student_purchase_record.objects.values()
        )  # 確認變成已付款了

        self.assertEqual(
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.count(),
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(id=1).available_remaining_minutes
            ),
            (
                1, 600
            )
        )  # 確認有正確更新

    
    def test_if_student_remaining_time_table_updated_after_unpaid_turned_into_paid_trial_set(self):
        '''
        這個函式用來測試，當學生付完款(試教方案)後，管理員或程式把該筆訂單的付款狀態設定為「已付款」後，
        學生的 student_remaining_minutes_of_each_purchased_lesson_set table 有沒有長出對應的資料。
        '''
        lesson_set = 'trial'
        post_data = {
            'userID':2,
            'teacherID':1,
            'lessonID':1,
            'sales_set': lesson_set,
            'total_amount_of_the_sales_set': int(self.lesson_post_data['price_per_hour'] * 10 * 0.9),
            'q_discount':0
        }  #測試 trial 看看是否成功
        self.client.post(path='/api/account_finance/storageOrder/', data=post_data)

        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,
            'unpaid',
            student_purchase_record.objects.values()
        )  # 目前應該是未付款的狀態

        # 如果我們將它設定為已付款，理論上應該會連動更新學生的 student_remaining_minutes_of_each_purchased_lesson_set
        the_student_purchase_record_object = \
            student_purchase_record.objects.get(id=1)
        the_student_purchase_record_object.payment_status = 'paid'
        the_student_purchase_record_object.save()

        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,
            'paid',
            student_purchase_record.objects.values()
        )  # 確認變成已付款了

        self.assertEqual(
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.count(),
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(id=1).available_remaining_minutes
            ),
            (
                1, 30
            )
        )  # 確認有正確更新

        
    def test_if_student_remaining_time_table_updated_after_unpaid_turned_into_paid_no_discount_set(self):
        '''
        這個函式用來測試，當學生付完款(單堂方案)後，管理員或程式把該筆訂單的付款狀態設定為「已付款」後，
        學生的 student_remaining_minutes_of_each_purchased_lesson_set table 有沒有長出對應的資料。
        '''
        lesson_set = 'no_discount'
        post_data = {
            'userID':2,
            'teacherID':1,
            'lessonID':1,
            'sales_set': lesson_set,
            'total_amount_of_the_sales_set': int(self.lesson_post_data['price_per_hour'] * 10 * 0.9),
            'q_discount':0
        }  #測試 no_discount 看看是否成功
        self.client.post(path='/api/account_finance/storageOrder/', data=post_data)

        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,
            'unpaid',
            student_purchase_record.objects.values()
        )  # 目前應該是未付款的狀態

        # 如果我們將它設定為已付款，理論上應該會連動更新學生的 student_remaining_minutes_of_each_purchased_lesson_set
        the_student_purchase_record_object = \
            student_purchase_record.objects.get(id=1)
        the_student_purchase_record_object.payment_status = 'paid'
        the_student_purchase_record_object.save()

        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,
            'paid',
            student_purchase_record.objects.values()
        )  # 確認變成已付款了

        self.assertEqual(
            (
                student_remaining_minutes_of_each_purchased_lesson_set.objects.count(),
                student_remaining_minutes_of_each_purchased_lesson_set.objects.get(id=1).available_remaining_minutes
            ),
            (
                1, 60
            )
        )  # 確認有正確更新
        

    def test_email_sending_new_order(self):
        #mail.outbox = [] # 清空暫存記憶裡的信, def結束會自動empty,有需要再用
        data_test = {'studentID':2, 'teacherID':1,'lessonID':1,
                    'lesson_set':'30:70' ,'total_lesson_set_price':100,
                    'email_pattern_name':'訂課匯款提醒',
                    'q_discount':20}

        self.assertIsNotNone(student_profile.objects.filter(auth_id=data_test['studentID']).first())
        self.assertIsNotNone(teacher_profile.objects.filter(auth_id=data_test['teacherID']).first())
        self.assertIsNotNone(lesson_info.objects.filter(id=data_test['lessonID']).first())

        e = email_manager()
        ret = e.system_email_new_order_and_payment_remind(**data_test)
        self.assertTrue(ret)
        # 確認程式有正確執行
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '訂課匯款提醒')
    
    def test_email_sending_receive_order_payment_when_unpaid_turned_into_paid(self):
        '''
        這個函式用來測試，當學生付完款(一般的方案)後，管理員或程式把該筆訂單的付款狀態設定為「已付款」後，
        要寄出一封email告訴學生我們收到款項了
        '''
        mail.outbox = []
        self.assertEqual(len(mail.outbox), 0)
        lesson_set = '10:90'
        post_data = {
            'userID':2,
            'teacherID':1,
            'lessonID':1,
            'sales_set': lesson_set,
            'total_amount_of_the_sales_set': int(self.lesson_post_data['price_per_hour'] * 10 * 0.9),
            'q_discount':0
        }  #先測試 10:90 看看是否成功
        self.client.post(path='/api/account_finance/storageOrder/', data=post_data)
        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,'unpaid',
            student_purchase_record.objects.values()
        )  # 目前應該是未付款的狀態

        # 如果我們將它設定為已付款，理論上要寄出一封確認信
        the_student_purchase_record_object = \
            student_purchase_record.objects.get(id=1)
        the_student_purchase_record_object.payment_status = 'paid'
        the_student_purchase_record_object.save()

        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,
            'paid',
            student_purchase_record.objects.values()
        )  # 確認變成已付款了
        
        self.assertEqual(len(mail.outbox), 2) # 這是第二封信, 建立訂單時會寄出第一封信
        self.assertEqual(mail.outbox[0].subject, '訂課匯款提醒')
        self.assertEqual(mail.outbox[1].subject, '收到款項提醒')


    def test_email_sending_receive_order_payment(self):
        #mail.outbox = [] # 清空暫存記憶裡的信, def結束會自動empty,有需要再用
        data_test = {'studentID':2, 'teacherID':1,'lessonID':1,
                    'lesson_set':'30:70' ,'total_lesson_set_price':100,
                    'email_pattern_name':'收到款項提醒',
                    'q_discount':20}

        self.assertIsNotNone(student_profile.objects.filter(auth_id=data_test['studentID']).first())
        self.assertIsNotNone(teacher_profile.objects.filter(auth_id=data_test['teacherID']).first())
        self.assertIsNotNone(lesson_info.objects.filter(id=data_test['lessonID']).first())

        mail.outbox = []
        e = email_manager()
        ret = e.system_email_new_order_and_payment_remind(**data_test)
        self.assertTrue(ret)
        # 確認程式有正確執行
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '收到款項提醒')



    def test_receive_user_payment_page(self):
        response = self.client.post(path='/api/account_finance/confirm_lesson_order_payment/')
        self.assertEqual(response.status_code, 200)
    def create_student_purchase_remain_minutes(self):
        response = self.client.post(path='/api/account_finance/create_lesson_order_minute/')
        self.assertEqual(response.status_code, 200)


@skip
class pure_email_send_test(TestCase):

    def test_email_could_send(self):
        self.client = Client()
        response = self.client.get('/api/account/send_email/')
        self.assertIn('Success', str(response.content, 'utf8'),
        str(response.content, 'utf8'))