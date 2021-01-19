from django.http import response
from django.test import TestCase, Client, RequestFactory
from account_finance.models import student_purchase_record
from account_finance.models import (student_remaining_minutes_of_each_purchased_lesson_set,
                            student_remaining_minutes_when_request_refund_each_purchased_lesson_set)
from account_finance.models import teacher_refund, student_refund
from account.models import student_profile, teacher_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info
from account_finance.email_sending import email_manager
from django.contrib.auth.models import Group
import os, shutil
from django.core import mail
from unittest import skip
from django.contrib.auth.models import User
from account.models import specific_available_time
from datetime import datetime, timedelta, date as date_function
import math
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
        # 建立3個學生
        self.test_student_name = ['test_student1@a.com','test_student2@a.com','test_student3@a.com']
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
        # 1號學生給q幣50元
        self.dummy_q = 50
        student1_obj = student_profile.objects.get(id=1)
        student1_obj.balance = self.dummy_q
        student1_obj.save()
        self.assertEqual(student_profile.objects.get(id=1).balance, 50)
        # 2號學生:q幣50元,預扣已有20元(表示他另一堂課花了20q幣來折抵)
        self.dummy_withhoding = 20
        student2_obj = student_profile.objects.get(id=2)
        student2_obj.balance = self.dummy_q
        student2_obj.withholding_balance = self.dummy_withhoding
        student2_obj.save()
        self.assertEqual(student_profile.objects.get(id=2).withholding_balance, 20)

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
        # 要建立課程才能測試
        data = {'userID':2,
        'teacherID':1,
        'lessonID':1,
        'sales_set': 'trial',#,'no_discount','30:70']
        'total_amount_of_the_sales_set': 69,
        'q_discount': 0}

        response = self.client.post(path='/api/account_finance/storageOrder/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1 # 建立1號訂單
            })
    
    def test_storege_order_student_use_Qcoin_with_no_withholding_balance(self):
        '''
        如果學生使用Q幣, 那送出訂單後使用的Q更新到他的profile中的withholding_balance_change.
        當他的預扣為0的情況
        '''
        data = {'userID':2,
        'teacherID':1,
        'lessonID':1,
        'sales_set': 'trial',#,'no_discount','30:70']
        'total_amount_of_the_sales_set': 69,
        'q_discount':20} # 要用20q幣折抵

        response = self.client.post(path='/api/account_finance/storageOrder/', data=data)
        # 1號學生有q幣 50元
        stu_withholding_balance = student_profile.objects.get(id=1).withholding_balance
        self.assertEqual(stu_withholding_balance, 20)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1 # 建立1號訂單
            })
    
    def test_storege_order_student_use_Qcoin_already_have_withholding_balance(self):
        '''
        如果學生使用Q幣, 那送出訂單後使用的Q更新到他的profile中的withholding_balance_change.
        當他的預扣不為0的情況
        '''
        data = {'userID':3,
        'teacherID':1,
        'lessonID':1,
        'sales_set': 'trial',#,'no_discount','30:70']
        'total_amount_of_the_sales_set': 69,
        'q_discount':20} # 要用20q幣折抵

        response = self.client.post(path='/api/account_finance/storageOrder/', data=data)
        # 2號學生有q幣 50元, 預扣已有20元
        stu_withholding_balance = student_profile.objects.get(id=2).withholding_balance
        self.assertEqual(stu_withholding_balance, 40)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {
                'status': 'success',
                'errCode': None,
                'errMsg': None,
                'data': 1 # 建立1號訂單
            })
       
    def test_student_withholding_balance_change_after_paid(self):
        '''
        當我們確認學生已繳費, unpaid改成paid之後,若有使用Q幣, 此時他的profile中的withholding_balance_change
        會歸零,而 balance會扣除。用1號學生測試,當他的預扣額
        '''
        lesson_set = '10:90' #先測試 10:90 看看是否成功
        use_q_coin = 20  #使用q幣
        post_data = {
            'userID':2,
            'teacherID':1,
            'lessonID':1,
            'sales_set': lesson_set,
            'total_amount_of_the_sales_set': int(self.lesson_post_data['price_per_hour'] * 10 * 0.9),
            'q_discount': use_q_coin
        } 
        self.client.post(path='/api/account_finance/storageOrder/', data=post_data)
        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,'unpaid')  # 目前應該是未付款的狀態
        student_obj = student_profile.objects.get(id=1)
        self.assertEqual(student_obj.balance, self.dummy_q)
        self.assertEqual(student_obj.withholding_balance, use_q_coin)
        student_purchase_obj = student_purchase_record.objects.get(id=1)
        student_purchase_obj.payment_status = 'paid'
        student_purchase_obj.save()
        self.assertEqual(
            student_purchase_record.objects.get(id=1).payment_status,'paid')  # 確認變成已付款
        
        # 如果我們將它設定為已付款，q_discount要同時從預扣額跟總額中扣除
        # 確認是否扣除
        student_obj = student_profile.objects.get(id=1)
        self.assertEqual(student_obj.balance, self.dummy_q - use_q_coin)
        self.assertEqual(student_obj.withholding_balance, 0)


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
            student_purchase_record.objects.filter(id=1).first().lesson_sales_set_id,
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
            'total_amount_of_the_sales_set': int(self.lesson_post_data['trial_class_price']),
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
            'total_amount_of_the_sales_set': int(self.lesson_post_data['price_per_hour']),
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

    def create_student_purchase_remain_minutes(self):
        response = self.client.post(path='/api/account_finance/create_lesson_order_minute/')
        self.assertEqual(response.status_code, 200)



class test_student_purchase_payment_status(TestCase):
    #def query_order_info_status1_unpaid(self):
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
        
        
        # 先取得兩個可預約日期，避免hard coded未來出錯
        # 時段我都設1,2,3,4,5，所以只要在其中就ok
        self.available_date_1 = specific_available_time.objects.filter(id=1).first().date
        # 建立1個學生
        student_post_data = {
                'regEmail': 'test_student_name',
                'regPwd': '00000000',
                'regName': 'test_student_name',
                'regBirth': '1990-12-25',
                'regGender': 1,
                'regRole': 'oneself',
                'regMobile': '0900-111111',
                'regNotifiemail': ''
            }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        self.assertEqual(User.objects.all().count() , 2) # 確認目前產生了2個user
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
        
        # 建立7筆訂單, 以測試7種狀態
        #  0-待付款/1-對帳中/2-已付款/3-退款中/4-已退款/5-有付款_取消訂單 6.未付款_取消訂單
        data = {'userID':2,
        'teacherID':1,
        'lessonID':1,
        'sales_set': 'no_discount',#'trial','30:70']
        'total_amount_of_the_sales_set': 800,
        'q_discount': 0}
        for num in range(0,7):
            response = self.client.post(path='/api/account_finance/storageOrder/', data=data)
        self.assertEqual(student_purchase_record.objects.all().count() , 7)
        # 訂單1 待付款, 為預設狀態,不用改
        # 訂單2 對帳中
        order = student_purchase_record.objects.get(id=2)
        order.payment_status = 'reconciliation'
        order.save()
        # 訂單3單純已付款
        # 將訂單3,4,5,6 改成已付款,要先改為付款才會長出計算剩餘時間的table、才能順利再改
        paid_order_num = [3,4,5,6]
        order_query_list = student_purchase_record.objects.filter(id__in =paid_order_num)
        for order in order_query_list:
            order.payment_status = 'reconciliation'
            order.save()

            order.payment_status = 'paid'
            order.save()
        # 訂單4 不改了
        # 訂單5 再改為已退款
        order = student_purchase_record.objects.get(id=5)
        order.payment_status = 'refund'
        order.save()
        # 訂單6 已付款後已取消
        order = student_purchase_record.objects.get(id=5)
        order.payment_status = 'cancel_after_paid'
        order.save()
        # 訂單7 未付款就已取消
        order = student_purchase_record.objects.get(id=5)
        order.payment_status = 'unpaid_cancel'
        order.save()
        # 確認已付款過的訂單都有長出剩餘時數
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.all().count(),
            len(paid_order_num), student_remaining_minutes_of_each_purchased_lesson_set.objects.values())
        self.assertEqual(student_purchase_record.objects.all().count(), 7)
        # 訂單8 測試'已付款的試教課程,取消付款'用的訂單
        data1 = {'userID':'2',
        'teacherID':'1',
        'lessonID':'1',
        'sales_set': 'trial',#'no_discount','30:70']
        'total_amount_of_the_sales_set': '69',
        'q_discount': '0'}
        #set_queryset = lesson_sales_sets.objects.filter(
        #    lesson_id=1, sales_set='trial', is_open= True)
        response = self.client.post(path='/api/account_finance/storageOrder/', data=data1)
        order = student_purchase_record.objects.get(id=8)
        order.payment_status = 'paid'
        order.save()
        self.assertEqual(student_purchase_record.objects.all().count(), 8)

        # 訂單9 測試'已付款的試教課程,取消付款'用的訂單
         
        print(type(math.ceil(self.lesson_post_data['price_per_hour']*10*0.9)))
        print(self.lesson_post_data['price_per_hour']*10*0.9)
        data1 = {'userID':'2',
        'teacherID':'1',
        'lessonID':'1',
        'sales_set': '10:90', 
        'total_amount_of_the_sales_set': str(math.ceil(int( 
                                self.lesson_post_data['price_per_hour'])*10*0.9)),# 取整數才可轉str
        'q_discount': '0'}
        response = self.client.post(path='/api/account_finance/storageOrder/', data=data1)
        
        self.assertEqual(student_purchase_record.objects.all().count(), 9,
            student_purchase_record.objects.values_list('id', flat=True))
        
        order = student_purchase_record.objects.get(id=9)
        order.payment_status = 'paid'
        order.save()
        
        #print(f'長度:{set_queryset}')
        #print(f'金額{set_queryset.first().total_amount_of_the_sales_set}')
        self.assertEqual(student_purchase_record.objects.all().count(), 9)



    def test_oreder_history_response(self):
        data = {
            'userID':'2',
            'token':'1',
            'type':'1'
        }
        response = self.client.post(path='/api/account_finance/studentOrderHistory/', data=data)
        self.assertEqual(student_purchase_record.objects.all().count(),9)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', str(response.content))
        #self.assertJSONEqual(
        #    str(response.content, encoding='utf8'),
        #    {
        #        'status': 'success',
                #'errCode': None,
                #'errMsg': None,
                #'data': 1 # 建立1號訂單
        #    })

    def test_student_edit_order_from_unpaid_to_paid(self):
        '''
        check update payment_status改成對帳中refunding, 且有存入銀行5碼,並有寄信給edony
        '''
        mail.outbox = [] # 清空前幾段test暫存記憶裡的信
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID': '1',
            'status_update': '0', # 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code': '11111'
        }
        response = self.client.post(path='/api/account_finance/studentEditOrder/', data=data)
        record = student_purchase_record.objects.get(id = 1)

        #self.assertEqual(student_purchase_record.objects.all().count() , 8)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', str(response.content))
        self.assertEqual(record.payment_status , 'refunding')
        self.assertEqual(record.part_of_bank_account_code, '11111')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '學生匯款通知信')
    

    def test_student_edit_order_when_paid_a_trial_request_a_refund(self):
        ''' 測試「已付款」的「試教」課程，學生申請退款 
        1. 計算是否有剩餘時間 2. 比對剩餘時間換算的金額是否正確 3.訂單狀態是否改為cancel_after_paid
        4. student_balance Q幣是否有增加 5. 剩餘時間的is_refunded有改為1 6. 順利長出退款時剩餘時間的紀錄'''
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID': '8',
            'status_update':'1',# 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code':'11111'}
        response = self.client.post(path='/api/account_finance/studentEditOrder/', data=data)
        self.assertIn('success', str(response.content))
        self.assertEqual(student_purchase_record.objects.get(id=8).payment_status, 
                        'refunded') # 確認訂單狀態有改
        # 檢查學生profile的Q幣金額是否正確
        self.assertEqual(student_profile.objects.get(auth_id = data['userID']).balance, 
                        self.lesson_post_data['trial_class_price'])
        # 檢查剩餘時間的is_refunded有改為1
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
            student_purchase_record_id=8).is_refunded,1)
        # 確認退款時剩餘時間紀錄有長出來
        self.assertEqual(student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.all().count(),1)
        info = student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.get(id=1)
        # 確認剩餘時間試30分鐘
        self.assertEqual(info.snapshot_available_remaining_minutes, 30)
        # 確認退款紀錄的Q幣 = 試教課程費用,有算對
        self.assertEqual(info.available_minutes_turn_into_q_points, self.lesson_post_data['trial_class_price'])

    @skip
    def test_if_set_still_can_be_booked_when_the_purchase_order_was_refunded(self):
        '''測試試教的課程已退款後是否還可以預約，理論上要不能預約，不能回success'''
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID': '8',
            'status_update':'1',# 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code':'11111'}
        # 先製作一個已退款的訂單
        response = self.client.post(path='/api/account_finance/studentEditOrder/', data=data)
        self.assertIn('success', str(response.content))
        record = student_purchase_record.objects.get(id=8)
        self.assertEqual(record.payment_status, 'refunded')
        # 嘗試預約
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'lessonID': '1',
            'bookingDateTime':f'{self.available_date_1}:1;'}
        response = self.client.post(path='/api/lesson/bookingLessons/', data=data)
        self.assertIn('success', str(response.content))



    def test_student_edit_order_when_paid_a_no_discount_request_a_refund(self):
        ''' 測試「已付款」買「一堂課」課程時，學生申請退款 
        1. 計算是否有剩餘時間 2. 比對剩餘時間換算的金額是否正確 3.訂單狀態是否改為cancel_after_paid
        4. student_balance Q幣是否有增加 5. 剩餘時間的is_refunded有改為1 6. 順利長出退款時剩餘時間的紀錄'''
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID': '4', # 已經paid的 no_discount課程
            'status_update':'1',# 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code':'11111'}
        response = self.client.post(path='/api/account_finance/studentEditOrder/', data=data)
        self.assertIn('success', str(response.content))
        self.assertEqual(student_purchase_record.objects.get(id=4).payment_status, 
                        'refunded') # 確認訂單狀態有改
        # 檢查學生profile的Q幣金額是否正確
        self.assertEqual(student_profile.objects.get(auth_id = data['userID']).balance, 
                        self.lesson_post_data['price_per_hour'])
        # 檢查剩餘時間的is_refunded有改為1
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
            student_purchase_record_id=4).is_refunded,1)
        # 確認退款時剩餘時間紀錄有長出來
        self.assertEqual(student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.all().count(),1)
        info = student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.get(id=1)
        # 確認剩餘時間是60分鐘
        self.assertEqual(info.snapshot_available_remaining_minutes, 60)
        # 確認退款紀錄的Q幣 = 單堂課程費用,有算對
        self.assertEqual(info.available_minutes_turn_into_q_points, 
                            self.lesson_post_data['price_per_hour'])
    
    @skip
    def test_if_set_still_can_be_booked_when_the_purchase_order_was_refunded(self):
        '''測試單堂的課程已退款後是否還可以預約，理論上要不能預約，不能回success'''
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID': '4',
            'status_update':'1',# 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code':'11111'}
        # 先製作一個已退款的訂單
        response = self.client.post(path='/api/account_finance/studentEditOrder/', data=data)
        self.assertIn('success', str(response.content))
        record = student_purchase_record.objects.get(id=4)
        self.assertEqual(record.payment_status, 'refunded')
        # 嘗試預約
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'lessonID': '1',
            'bookingDateTime':f'{self.available_date_1}:1;'}
        response = self.client.post(path='/api/lesson/bookingLessons/', data=data)
        self.assertIn('success', str(response.content))
   
   
    def test_student_edit_order_when_paid_set_discount_request_a_refund(self):
        ''' 測試「已付款」買「多堂課」課程時，學生申請退款。此時學生尚未上過課
        1. 計算是否有剩餘時間 2. 比對剩餘時間換算的金額是否正確 3.訂單狀態是否改為cancel_after_paid
        4. student_balance Q幣是否有增加 5. 剩餘時間的is_refunded有改為1 6. 順利長出退款時剩餘時間的紀錄'''
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID': '9', # 已經paid的 多堂discount課程
            'status_update':'1',# 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code':'11111'}
        response = self.client.post(path='/api/account_finance/studentEditOrder/', data=data)
        self.assertIn('success', str(response.content))
        self.assertEqual(student_purchase_record.objects.get(id=9).payment_status,'refunded') # 確認訂單狀態有改
        # 檢查學生profile的Q幣金額是否正確
        test_record_obj = student_purchase_record.objects.get(id=9)# 第九筆訂單
        set_obj = lesson_sales_sets.objects.get(id=test_record_obj.lesson_sales_set_id)
        print(set_obj.sales_set)
        total_set_time = int(set_obj.sales_set.split(':')[0]) #*60 # 小時轉分鐘
        set_dicount = int(set_obj.sales_set.split(':')[1])/100 # 折數
        test_price = total_set_time*set_dicount*self.lesson_post_data['price_per_hour']

        self.assertEqual(student_profile.objects.get(auth_id = data['userID']).balance, 
                        test_price)
        # 檢查剩餘時間的is_refunded有改為1
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
            student_purchase_record_id=9).is_refunded,1)
        # 確認退款時剩餘時間紀錄有長出來
        self.assertEqual(student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.all().count(),1)
        info = student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.get(id=1)
        # 確認剩餘時間是方案的分鐘
        self.assertEqual(info.snapshot_available_remaining_minutes, int(set_obj.sales_set.split(':')[0])*60) # 小時轉分鐘)
        # 確認退款紀錄的Q幣有算對
        self.assertEqual(info.available_minutes_turn_into_q_points, 
                           test_price)

    @skip
    def test_if_set_still_can_be_booked_when_the_purchase_order_was_refunded(self):
        '''測試「已付款」買「多堂課」時的課程已退款後是否還可以預約，理論上要不能預約，不能回success'''
        
        data1 = {'userID':'2',
        'teacherID':'1',
        'lessonID':'1',
        'sales_set': '10:90', 
        'total_amount_of_the_sales_set': str(math.ceil(int( 
                                self.lesson_post_data['price_per_hour'])*10*0.9)),# 取整數才可轉str
        'q_discount': '0'}
        response = self.client.post(path='/api/account_finance/storageOrder/', data=data1)
        
        
        order = student_purchase_record.objects.filter(student_auth_id = data1['userID']).order_by('updated_time')
        order.payment_status = 'paid'
        order.save()
        
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID': '9',
            'status_update':'1',# 0-付款完成/1-申請退款/2-申請取消
            'part_of_bank_account_code':'11111'}
        # 先製作一個已退款的訂單
        response = self.client.post(path='/api/account_finance/studentEditOrder/', data=data)
        self.assertIn('success', str(response.content))
        record = student_purchase_record.objects.get(id=9)
        self.assertEqual(record.payment_status, 'refunded')
        # 嘗試預約
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'lessonID': '1',
            'bookingDateTime':f'{self.available_date_1}:1;'}
        response = self.client.post(path='/api/lesson/bookingLessons/', data=data)
        self.assertIn('success', str(response.content))


    def test_student_edit_order_cancel_before_paid(self):
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID':1,
            'status_update':2,# 0-付款完成/1-申請退款/2-申請取消
            'user5_bank_code':11111
        }
        response = self.client.post(path='/api/account_finance/studentOrderHistory/', data=data)
        self.assertEqual(response.status_code, 200)
    
    
    def test_student_edit_order_cancel_after_paid(self):
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID':1,
            'status_update':2,
            'user5_bank_code':11111
        }
        response = self.client.post(path='/api/account_finance/studentOrderHistory/', data=data)
        self.assertEqual(response.status_code, 200)


@skip
class LESSON_SALES_HISTORY_TEST(TestCase):
    
    
    def setUp(self):
        self.client = Client()        
        Group.objects.bulk_create(
            [
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ]
        )
        self.test_teacher_name1 = 'test_teacher1_user@test.com'
        teacher_post_data = {
            'regEmail': self.test_teacher_name1,
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:1,2,3,4,5;4:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        
        self.test_teacher_name2 = 'test_teacher2_user@test.com'
        teacher_post_data['regEmail'] = self.test_teacher_name2,
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)

        self.test_teacher_name3 = 'test_teacher3_user@test.com'
        teacher_post_data['regEmail'] = self.test_teacher_name3,
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建了3個老師
        
        self.test_student_name1 = 'test_student1@a.com'
        student_post_data = {
            'regEmail': self.test_student_name1,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name2 = 'test_student2@a.com'
        student_post_data['regEmail'] = self.test_student_name2
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name3 = 'test_student3@a.com'
        student_post_data['regEmail'] = self.test_student_name3
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        # 建了3個學生
        
        # 建立課程
        self.lesson_post_data1 = {
            'userID': teacher_profile.objects.get(id=1).auth_id,   # 這是老師1的auth_id
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
        self.client.post(path='/api/lesson/createOrEditLesson/', data=self.lesson_post_data1)

        self.lesson_post_data2 = {
            'userID': teacher_profile.objects.get(id=2).auth_id,   # 這是老師2的auth_id
            'action': 'createLesson',
            'big_title': 'big_title',
            'little_title': 'test',
            'title_color': '#000000',
            'background_picture_code': 1,
            'background_picture_path': '',
            'lesson_title': 'test',
            'price_per_hour': 1200,
            'discount_price': '5:90;20:80;30:70;',
            'selling_status': 'selling',
            'lesson_has_one_hour_package': True,
            'trial_class_price': -999,
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
        self.client.post(path='/api/lesson/createOrEditLesson/', data=self.lesson_post_data2)

        # 先取得兩個可預約日期，避免hard coded未來出錯
        # 時段我都設1,2,3,4,5，所以只要在其中就ok
        self.available_date_1_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1)).first().date
        self.available_date_2_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1))[1].date
        self.available_date_3_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1))[2].date
        self.available_date_4_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1))[3].date
        self.available_date_5_t1 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=1))[4].date

        self.available_date_11_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[10].date
        self.available_date_12_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[11].date
        self.available_date_13_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[12].date
        self.available_date_4_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[3].date
        self.available_date_15_t2 = specific_available_time.objects.filter(teacher_model=teacher_profile.objects.get(id=2))[14].date


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name1)
            shutil.rmtree('user_upload/students/' + self.test_student_name2)
            shutil.rmtree('user_upload/students/' + self.test_student_name3)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name1)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name2)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name3)
        except:
            pass

    
    def test_get_lesson_sales_history_exist(self):
        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'
        }
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)

        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))


    def test_get_lesson_sales_history_failed_when_teacher_doesnt_exist(self):
        query_history_post_data = {
            'userID': 99,
            'type': 'teacher'
        }
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)

        self.assertIn('failed', str(response.content, "utf8"), str(response.content, "utf8"))

    
    def test_get_lesson_sales_history_failed_when_teacher_exist_and_no_lesson(self):
        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=3).auth_id,
            'type': 'teacher'
        }
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)

        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"data": null', str(response.content, "utf8"), str(response.content, "utf8"))


    def test_get_lesson_sales_history_when_teacher_exist_and_has_purchased_lesson_sales_set(self):

        # 先讓學生購買課程方案
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(10*800*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()
        # 理論上現在已經購買、付款完成了

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'
        }
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)

        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"purchased_record_id"', str(response.content, "utf8"))
        self.assertIn('"purchased_lesson_sales_set_status"', str(response.content, "utf8"))
        self.assertIn('"created_date"', str(response.content, "utf8"))
        self.assertIn('"student_nickname"', str(response.content, "utf8"))
        self.assertIn('"student_auth_id"', str(response.content, "utf8"))
        self.assertIn('"lesson_title"', str(response.content, "utf8"))
        self.assertIn('"lessonID"', str(response.content, "utf8"))
        self.assertIn('"lesson_sales_set"', str(response.content, "utf8"))
        self.assertIn('"total_amount"', str(response.content, "utf8"))
        self.assertIn('"available_remaining_minutes"', str(response.content, "utf8"))
        self.assertIn('"unconsumed_minutes"', str(response.content, "utf8"))
        self.assertIn('"is_selling"', str(response.content, "utf8"))


    def test_get_lesson_sales_history_when_teacher_exist_and_has_purchased_lesson_and_its_lessons_counting_is_right(self):
        '''
        這裏測試當學生連續買了兩門課程後，是否data中真的有而且只有兩筆資料。
        '''
        # 先讓學生購買2門課程方案
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        purchase_post_data['sales_set'] = '10:90'
        purchase_post_data['total_amount_of_the_sales_set'] = int(10*800*0.9)
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        # 此時因為還沒付款，應該是找不到對應的data
        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)

        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertIn('"data": null', str(response.content, "utf8"), str(response.content, "utf8"))

        # 先來付款第1門課程
        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)

        self.assertIn('success', str(response.content, "utf8"), str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count('"total_amount"'))

        # 再付款第2門課程
        the_purchase_object = \
            student_purchase_record.objects.get(id=2)
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        self.assertEqual(2, str(response.content, "utf8").count('"total_amount"'))
        # 確認有抓到第二門購買的紀錄

    
    def test_get_lesson_sales_history_when_teacher_exist_and_has_purchased_trial_lesson_and_its_content_is_right(self):
        '''
        這裏測試當學生買了試教課程後，回傳的資訊是否正確。
        '''
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        # 先來付款這個試教課程
        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        
        that_student_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                student_purchase_record_id = student_purchase_record.objects.first().id
            )
        available_remaining_minutes = that_student_remaining_minutes_object.available_remaining_minutes
        unconsumed_minutes = that_student_remaining_minutes_object.available_remaining_minutes + \
            that_student_remaining_minutes_object.confirmed_consumed_minutes
        
        # 先確認一下回傳數量是對的
        self.assertEqual(1, str(response.content, "utf8").count('"total_amount"'))
        # 再確認購買紀錄的id是正確的
        self.assertIn('"purchased_record_id": 1', str(response.content, "utf8"))
        self.assertIn('"purchased_lesson_sales_set_status": "on_going"', str(response.content, "utf8"))
        self.assertIn(f'"created_date": "{date_function.today()}"', str(response.content, "utf8"))
        self.assertIn(f'"student_nickname": "{student_profile.objects.first().nickname}"', str(response.content, "utf8"))
        self.assertIn(f'"student_auth_id": {student_profile.objects.first().auth_id}', str(response.content, "utf8"))
        self.assertIn(f'"lesson_title": "{lesson_info.objects.first().lesson_title}"', str(response.content, "utf8"))
        self.assertIn(f'"lessonID": {lesson_info.objects.first().id}', str(response.content, "utf8"))
        self.assertIn(f'"lesson_sales_set": "{lesson_sales_sets.objects.get(id=the_purchase_object.lesson_sales_set_id).sales_set}"', str(response.content, "utf8"))
        self.assertIn(f'"total_amount": {lesson_sales_sets.objects.get(id=the_purchase_object.lesson_sales_set_id).total_amount_of_the_sales_set}', str(response.content, "utf8"))
        self.assertIn(f'"available_remaining_minutes": {available_remaining_minutes}', str(response.content, "utf8"))
        self.assertIn(f'"unconsumed_minutes": {unconsumed_minutes}', str(response.content, "utf8"))
        self.assertIn(f'"is_selling": true', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_1 {str(response.content, "utf8")}')

        # 接下來測試一下當 老師不繼續開放 試教課程 購買時，看看 is_selling 會否變成 false
        self.lesson_post_data1['trial_class_price'] = -999
        self.lesson_post_data1['action'] = 'editLesson'
        self.lesson_post_data1['lessonID'] = lesson_info.objects.filter(\
            teacher=teacher_profile.objects.get(id=1)).first().id
        
        response = \
            self.client.post(path='/api/lesson/createOrEditLesson/', data=self.lesson_post_data1)
        self.assertIn('success', str(response.content, "utf8"))

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        self.assertIn(f'"is_selling": false', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_2 {str(response.content, "utf8")}')

        # 接下來測試一下 如果將學生 的 時數都消耗掉，則其 
        # purchased_lesson_sales_set_status 應該會變成 finished
        that_student_remaining_minutes_object.confirmed_consumed_minutes += \
            that_student_remaining_minutes_object.available_remaining_minutes + that_student_remaining_minutes_object.withholding_minutes
        that_student_remaining_minutes_object.available_remaining_minutes = 0
        that_student_remaining_minutes_object.withholding_minutes = 0
        that_student_remaining_minutes_object.save()

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        self.assertIn('"purchased_lesson_sales_set_status": "finished"', str(response.content, "utf8"))
        self.assertIn(f'"is_selling": false', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_3 {str(response.content, "utf8")}')


    def test_get_lesson_sales_history_when_teacher_exist_and_has_purchased_no_discount_lesson_and_its_content_is_right(self):
        '''
        這裏測試當學生買了一般課程後，回傳的資訊是否正確。
        '''
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': 'no_discount',
            'total_amount_of_the_sales_set': 800,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        # 先來付款這個試教課程
        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        
        that_student_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                student_purchase_record_id = student_purchase_record.objects.first().id
            )
        available_remaining_minutes = that_student_remaining_minutes_object.available_remaining_minutes
        unconsumed_minutes = that_student_remaining_minutes_object.available_remaining_minutes + \
            that_student_remaining_minutes_object.confirmed_consumed_minutes
        
        # 先確認一下回傳數量是對的
        self.assertEqual(1, str(response.content, "utf8").count('"total_amount"'))
        # 再確認購買紀錄的id是正確的
        self.assertIn('"purchased_record_id": 1', str(response.content, "utf8"))
        self.assertIn('"purchased_lesson_sales_set_status": "on_going"', str(response.content, "utf8"))
        self.assertIn(f'"created_date": "{date_function.today()}"', str(response.content, "utf8"))
        self.assertIn(f'"student_nickname": "{student_profile.objects.first().nickname}"', str(response.content, "utf8"))
        self.assertIn(f'"student_auth_id": {student_profile.objects.first().auth_id}', str(response.content, "utf8"))
        self.assertIn(f'"lesson_title": "{lesson_info.objects.first().lesson_title}"', str(response.content, "utf8"))
        self.assertIn(f'"lessonID": {lesson_info.objects.first().id}', str(response.content, "utf8"))
        self.assertIn(f'"lesson_sales_set": "{lesson_sales_sets.objects.get(id=the_purchase_object.lesson_sales_set_id).sales_set}"', str(response.content, "utf8"))
        self.assertIn(f'"total_amount": {lesson_sales_sets.objects.get(id=the_purchase_object.lesson_sales_set_id).total_amount_of_the_sales_set}', str(response.content, "utf8"))
        self.assertIn(f'"available_remaining_minutes": {available_remaining_minutes}', str(response.content, "utf8"))
        self.assertIn(f'"unconsumed_minutes": {unconsumed_minutes}', str(response.content, "utf8"))
        self.assertIn(f'"is_selling": true', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_no_discount_1 {str(response.content, "utf8")}')

        # 接下來測試一下當 老師不繼續開放 no_discount 購買時，看看 is_selling 會否變成 false
        self.lesson_post_data1['lesson_has_one_hour_package'] = False
        self.lesson_post_data1['action'] = 'editLesson'
        self.lesson_post_data1['lessonID'] = lesson_info.objects.filter(\
            teacher=teacher_profile.objects.get(id=1)).first().id
        
        response = \
            self.client.post(path='/api/lesson/createOrEditLesson/', data=self.lesson_post_data1)
        self.assertIn('success', str(response.content, "utf8"))

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        self.assertIn(f'"is_selling": false', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_no_discount_2 {str(response.content, "utf8")}')

        # 接下來測試一下 如果將學生 的 時數都消耗掉，則其 
        # purchased_lesson_sales_set_status 應該會變成 finished
        that_student_remaining_minutes_object.confirmed_consumed_minutes += \
            that_student_remaining_minutes_object.available_remaining_minutes + that_student_remaining_minutes_object.withholding_minutes
        that_student_remaining_minutes_object.available_remaining_minutes = 0
        that_student_remaining_minutes_object.withholding_minutes = 0
        that_student_remaining_minutes_object.save()

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        self.assertIn('"purchased_lesson_sales_set_status": "finished"', str(response.content, "utf8"))
        self.assertIn(f'"is_selling": false', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_no_discount_3 {str(response.content, "utf8")}')
        

    def test_get_lesson_sales_history_when_teacher_exist_and_has_purchased_common_lessons_and_its_content_is_right(self):
        '''
        這裏測試當學生買了一般套裝課程後，回傳的資訊是否正確。
        '''
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': '10:90',
            'total_amount_of_the_sales_set': int(10*800*0.9),
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)

        # 先來付款
        the_purchase_object = \
            student_purchase_record.objects.first()
        the_purchase_object.payment_status = 'paid'
        the_purchase_object.save()

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        
        that_student_remaining_minutes_object = \
            student_remaining_minutes_of_each_purchased_lesson_set.objects.get(
                student_purchase_record_id = student_purchase_record.objects.first().id
            )
        available_remaining_minutes = that_student_remaining_minutes_object.available_remaining_minutes
        unconsumed_minutes = that_student_remaining_minutes_object.available_remaining_minutes + \
            that_student_remaining_minutes_object.confirmed_consumed_minutes
        
        # 先確認一下回傳數量是對的
        self.assertEqual(1, str(response.content, "utf8").count('"total_amount"'))
        # 再確認購買紀錄的id是正確的
        self.assertIn('"purchased_record_id": 1', str(response.content, "utf8"))
        self.assertIn('"purchased_lesson_sales_set_status": "on_going"', str(response.content, "utf8"))
        self.assertIn(f'"created_date": "{date_function.today()}"', str(response.content, "utf8"))
        self.assertIn(f'"student_nickname": "{student_profile.objects.first().nickname}"', str(response.content, "utf8"))
        self.assertIn(f'"student_auth_id": {student_profile.objects.first().auth_id}', str(response.content, "utf8"))
        self.assertIn(f'"lesson_title": "{lesson_info.objects.first().lesson_title}"', str(response.content, "utf8"))
        self.assertIn(f'"lessonID": {lesson_info.objects.first().id}', str(response.content, "utf8"))
        self.assertIn(f'"lesson_sales_set": "{lesson_sales_sets.objects.get(id=the_purchase_object.lesson_sales_set_id).sales_set}"', str(response.content, "utf8"))
        self.assertIn(f'"total_amount": {lesson_sales_sets.objects.get(id=the_purchase_object.lesson_sales_set_id).total_amount_of_the_sales_set}', str(response.content, "utf8"))
        self.assertIn(f'"available_remaining_minutes": {available_remaining_minutes}', str(response.content, "utf8"))
        self.assertIn(f'"unconsumed_minutes": {unconsumed_minutes}', str(response.content, "utf8"))
        self.assertIn(f'"is_selling": true', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_common_1 {str(response.content, "utf8")}')

        # 接下來測試一下當 老師不繼續開放 10:90 購買時，看看 is_selling 會否變成 false
        self.lesson_post_data1['sales_set'] = '20:80'
        self.lesson_post_data1['action'] = 'editLesson'
        self.lesson_post_data1['lessonID'] = lesson_info.objects.filter(\
            teacher=teacher_profile.objects.get(id=1)).first().id
        
        response = \
            self.client.post(path='/api/lesson/createOrEditLesson/', data=self.lesson_post_data1)
        self.assertIn('success', str(response.content, "utf8"))

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        self.assertIn(f'"is_selling": false', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_common_2 {str(response.content, "utf8")}')

        # 接下來測試一下 如果將學生 的 時數都消耗掉，則其 
        # purchased_lesson_sales_set_status 應該會變成 finished
        that_student_remaining_minutes_object.confirmed_consumed_minutes += \
            that_student_remaining_minutes_object.available_remaining_minutes + that_student_remaining_minutes_object.withholding_minutes
        that_student_remaining_minutes_object.available_remaining_minutes = 0
        that_student_remaining_minutes_object.withholding_minutes = 0
        that_student_remaining_minutes_object.save()

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        self.assertIn('"purchased_lesson_sales_set_status": "finished"', str(response.content, "utf8"))
        self.assertIn(f'"is_selling": false', str(response.content, "utf8"))
        print(f'test_lesson_and_its_content_is_right_common_3 {str(response.content, "utf8")}')


    def test_get_lesson_sales_history_when_teacher_exist_and_multi_students_purchased_lesson_sets(self):
        '''
        這裏測試當複數學生買了不同課程後，回傳的資訊是否正確。
        '''
        # 先讓學生1購買3門課 >> trial, no_discount, 1:90，並且消耗trial
        purchase_post_data = {
            'userID':student_profile.objects.first().auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        purchase_post_data['sales_set'] = 'no_discount'
        purchase_post_data['total_amount_of_the_sales_set'] = 800
        purchase_post_data['q_discount'] = 200  # 試試看200q幣付款
        response = self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        self.assertIn('success', str(response.content, "utf8"))  # 用了Q幣，試試看有沒有成功
        purchase_post_data['sales_set'] = '10:90'
        purchase_post_data['total_amount_of_the_sales_set'] = int(10*800*0.9)
        purchase_post_data['q_discount'] = 0
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 買完三門課程了，接下來來付款

        # 先來付款
        for each_id in range(1, 4):
            the_purchase_obj = \
                student_purchase_record.objects.get(id=each_id)
            the_purchase_obj.payment_status = 'paid'
            the_purchase_obj.save()
        self.assertEqual(3, 
            student_remaining_minutes_of_each_purchased_lesson_set.objects.count())

        # 接著讓學生2號購買 trial 跟 20:80
        purchase_post_data = {
            'userID':student_profile.objects.get(id=2).auth_id,
            'teacherID':teacher_profile.objects.first().auth_id,
            'lessonID':lesson_info.objects.first().id,
            'sales_set': 'trial',
            'total_amount_of_the_sales_set': 69,
            'q_discount':0}
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        purchase_post_data['sales_set'] = '20:80'
        purchase_post_data['total_amount_of_the_sales_set'] = int(20*800*0.8)
        self.client.post(path='/api/account_finance/storageOrder/', data=purchase_post_data)
        # 付款
        for each_id in range(4, 6):
            the_purchase_obj = \
                student_purchase_record.objects.get(id=each_id)
            the_purchase_obj.payment_status = 'paid'
            the_purchase_obj.save()
        self.assertEqual(5, 
            student_remaining_minutes_of_each_purchased_lesson_set.objects.count())

        query_history_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher'}
        response = \
            self.client.post(path='/api/account_finance/getLessonSalesHistory/', data=query_history_post_data)
        # 先確認一下回傳數量是對的
        self.assertEqual(5, str(response.content, "utf8").count('"total_amount"'))
        self.assertEqual(2, str(response.content, "utf8").count(f'"student_auth_id": {student_profile.objects.get(id=2).auth_id}'))
        self.assertEqual(2, str(response.content, "utf8").count(f'"lesson_sales_set": "trial"'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"lesson_sales_set": "10:90"'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"lesson_sales_set": "no_discount"'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"lesson_sales_set": "20:80"'))



class Q_POINTS_WITHDRAWAL_TEST(TestCase):
    '''
    用來測試Q幣轉現金到戶頭的機制是否正確運作
    '''
    def setUp(self):
        self.client = Client()        
        Group.objects.bulk_create(
            [
                Group(name='test_student'),
                Group(name='test_teacher'),
                Group(name='formal_teacher'),
                Group(name='formal_student'),
                Group(name='edony')
            ]
        )
        self.test_teacher_name1 = 'test_teacher1_user@test.com'
        teacher_post_data = {
            'regEmail': self.test_teacher_name1,
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
            'teacher_general_availabale_time': '0:1,2,3,4,5;1:1,2,3,4,5;4:1,2,3,4,5;'
        }
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        
        self.test_teacher_name2 = 'test_teacher2_user@test.com'
        teacher_post_data['regEmail'] = self.test_teacher_name2,
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)

        self.test_teacher_name3 = 'test_teacher3_user@test.com'
        teacher_post_data['regEmail'] = self.test_teacher_name3,
        self.client.post(path='/api/account/signupTeacher/', data=teacher_post_data)
        # 建了3個老師
        
        self.test_student_name1 = 'test_student1@a.com'
        student_post_data = {
            'regEmail': self.test_student_name1,
            'regPwd': '00000000',
            'regName': 'test_student_name',
            'regBirth': '1990-12-25',
            'regGender': 1,
            'regRole': 'oneself',
            'regMobile': '0900-111111',
            'regNotifiemail': ''
        }
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name2 = 'test_student2@a.com'
        student_post_data['regEmail'] = self.test_student_name2
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)

        self.test_student_name3 = 'test_student3@a.com'
        student_post_data['regEmail'] = self.test_student_name3
        self.client.post(path='/api/account/signupStudent/', data=student_post_data)
        # 建了3個學生


    def tearDown(self):
        # 刪掉(如果有的話)產生的資料夾
        try:
            shutil.rmtree('user_upload/students/' + self.test_student_name1)
            shutil.rmtree('user_upload/students/' + self.test_student_name2)
            shutil.rmtree('user_upload/students/' + self.test_student_name3)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name1)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name2)
            shutil.rmtree('user_upload/teachers/' + self.test_teacher_name2)
        except:
            pass


    def test_withdraw_q_points_exists(self):
        # 測試該連結/api存在
        withdrawal_post_data = {
            'bank_code': '009',
            'bank_name': '彰化銀行',
            'bank_account_code': '222540508714',
            'action': 'only_editting'}
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertEqual(200, response.status_code)


    def test_withdraw_q_points_only_editting_teacher_and_student_work(self):
        # 測試老師能夠成功編輯帳戶
        withdrawal_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher',
            'bank_code': '009',
            'bank_name': '彰化銀行',
            'bank_account_code': '222540508714',
            'action': 'only_editting'}
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        teacher_1 = teacher_profile.objects.get(id=1)
        self.assertEqual(
            ('彰化銀行', '009', '222540508714'),
            (teacher_1.bank_name, teacher_1.bank_code, teacher_1.bank_account_code),
            teacher_profile.objects.values()
        )

        withdrawal_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher',
            'bank_code': '822',
            'bank_name': '中國信託商業銀行',
            'bank_account_code': '123456789101',
            'action': 'only_editting'}
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        teacher_1 = teacher_profile.objects.get(id=1)
        self.assertEqual(
            ('中國信託商業銀行', '822', '123456789101'),
            (teacher_1.bank_name, teacher_1.bank_code, teacher_1.bank_account_code),
            teacher_profile.objects.values()
        )

        # 測試學生3能夠成功編輯帳戶
        withdrawal_post_data = {
            'userID': student_profile.objects.get(id=3).auth_id,
            'type': 'student',
            'bank_code': '123',
            'bank_name': 'XXX銀行',
            'bank_account_code': '4569871235840',
            'action': 'only_editting'}
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        student_1 = student_profile.objects.get(id=3)
        self.assertEqual(
            (withdrawal_post_data['bank_name'], withdrawal_post_data['bank_code'], withdrawal_post_data['bank_account_code']),
            (student_1.bank_name, student_1.bank_code, student_1.bank_account_code),
            student_profile.objects.values()
        )

        # 測試type別不同會出錯
        withdrawal_post_data['type'] = 'teacher',
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('failed', str(response.content, "utf8"))

    
    def test_withdraw_q_points_withdrawal_teacher_and_student_work(self):
        # 測試老師能夠成功發起匯款訊息
        withdrawal_post_data = {
            'userID': teacher_profile.objects.get(id=1).auth_id,
            'type': 'teacher',
            'bank_code': '009',
            'bank_name': '彰化銀行',
            'bank_account_code': '222540508714',
            'action': 'withdrawal_after_editting'}
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertIn('"errCode": "5"', str(response.content, "utf8"))
        # 沒填寫匯款金額
        
        withdrawal_post_data['amount'] = 1000
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertIn('"errCode": "3"', str(response.content, "utf8"))
        # 餘額不足

        teacher_1 = teacher_profile.objects.get(id=1)
        teacher_1.balance = 1500
        teacher_1.save()
        # 加值個1500

        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertEqual(1, teacher_refund.objects.count())

        # 測試個人資訊是否有改變
        teacher_1 = teacher_profile.objects.get(id=1)
        self.assertEqual(
            (500, 1000),
            (teacher_1.balance, teacher_1.withholding_balance),
            teacher_profile.objects.values().get(id=1))

        # 再匯一筆，測試有沒有手續費
        withdrawal_post_data['amount'] = 500
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertIn('"errCode": "3"', str(response.content, "utf8"))
        # 餘額不足

        withdrawal_post_data['amount'] = 470
        self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        teacher_1 = teacher_profile.objects.get(id=1)
        self.assertEqual(
            (0, 1500),
            (teacher_1.balance, teacher_1.withholding_balance),
            teacher_profile.objects.values().get(id=1))


        # 測試學生能夠成功發起匯款訊息
        withdrawal_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'type': 'student',
            'bank_code': '009',
            'bank_name': '彰化銀行',
            'bank_account_code': '222540508714',
            'action': 'withdrawal_after_editting'}
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertIn('"errCode": "6"', str(response.content, "utf8"))
        # 沒填寫匯款金額
        
        withdrawal_post_data['amount'] = 1000
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertIn('"errCode": "4"', str(response.content, "utf8"))
        # 餘額不足

        student_2 = student_profile.objects.get(id=2)
        student_2.balance = 1500
        student_2.save()
        # 加值個1500

        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertEqual(1, student_refund.objects.count())

        # 測試個人資訊是否有改變
        student_2 = student_profile.objects.get(id=2)
        self.assertEqual(
            (500, 1000),
            (student_2.balance, student_2.withholding_balance),
            student_profile.objects.values().get(id=2))

        # 再匯一筆，測試有沒有手續費
        withdrawal_post_data['amount'] = 500
        response = \
            self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        self.assertIn('failed', str(response.content, "utf8"))
        self.assertIn('"errCode": "4"', str(response.content, "utf8"))
        # 餘額不足

        withdrawal_post_data['amount'] = 470
        self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        student_2 = student_profile.objects.get(id=2)
        self.assertEqual(
            (0, 1500),
            (student_2.balance, student_2.withholding_balance),
            student_profile.objects.values().get(id=2))


    def test_withdrawal_history_work(self):
        '''
        用來測試 老師/學生 查詢Q幣退款歷史紀錄 運作正常
        '''
        # 先查詢學生空資料
        query_history_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'type': 'student',
        }
        response = \
            self.client.post(path='/api/account_finance/getQPointsWtihdrawalHistory/', data=query_history_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"data": null', str(response.content, "utf8"))

        # 學生2 加值一點錢
        student_2 = student_profile.objects.get(id=2)
        student_2.balance = 5000
        student_2.save()

        # 學生2提款 2200
        withdrawal_post_data = {
            'userID': student_profile.objects.get(id=2).auth_id,
            'type': 'student',
            'bank_code': '009',
            'amount': 2200,
            'bank_name': '彰化銀行',
            'bank_account_code': '222540508714',
            'action': 'withdrawal_after_editting'}
        self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)

        # 查詢資料
        response = \
            self.client.post(path='/api/account_finance/getQPointsWtihdrawalHistory/', data=query_history_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count(f'"amount": 2200'), str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count(f'"withdrawal_status": "unpaid"'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"txn_fee": 0'))

        # 學生2 再提款 2500
        withdrawal_post_data['amount'] = 2500
        self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        # 查詢資料
        response = \
            self.client.post(path='/api/account_finance/getQPointsWtihdrawalHistory/', data=query_history_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count(f'"amount": 2200'), str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count(f'"amount": 2500'), str(response.content, "utf8"))
        self.assertEqual(2, str(response.content, "utf8").count(f'"withdrawal_status": "unpaid"'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"txn_fee": 0'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"txn_fee": 30'))

        # 更改第二筆資料付款狀態
        student_refund.objects.filter(
            student_auth_id=student_profile.objects.get(id=2).auth_id, refund_amount=2500).update(refund_status='paid')

        response = \
            self.client.post(path='/api/account_finance/getQPointsWtihdrawalHistory/', data=query_history_data)
        self.assertEqual(1, str(response.content, "utf8").count(f'"withdrawal_status": "unpaid"'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"withdrawal_status": "paid"'))


        # 查詢老師空資料
        query_history_data = {
            'userID': teacher_profile.objects.get(id=3).auth_id,
            'type': 'teacher',
        }
        response = \
            self.client.post(path='/api/account_finance/getQPointsWtihdrawalHistory/', data=query_history_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertIn('"data": null', str(response.content, "utf8"))

        # 老師3 加值一點錢
        teacher_3 = teacher_profile.objects.get(id=3)
        teacher_3.balance = 15000
        teacher_3.save()

        # 老師3 提款 8000
        withdrawal_post_data = {
            'userID': teacher_profile.objects.get(id=3).auth_id,
            'type': 'teacher',
            'bank_code': '109',
            'amount': 8000,
            'bank_name': '彰化銀行',
            'bank_account_code': '222540508714',
            'action': 'withdrawal_after_editting'}
        self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)

        # 查詢資料
        response = \
            self.client.post(path='/api/account_finance/getQPointsWtihdrawalHistory/', data=query_history_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count(f'"amount": 8000'), str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count(f'"withdrawal_status": "unpaid"'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"txn_fee": 0'))

        # 老師3 再提款 6000
        withdrawal_post_data['amount'] = 6000
        self.client.post(path='/api/account_finance/withdrawQPoints/', data=withdrawal_post_data)
        # 查詢資料
        response = \
            self.client.post(path='/api/account_finance/getQPointsWtihdrawalHistory/', data=query_history_data)
        self.assertIn('success', str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count(f'"amount": 8000'), str(response.content, "utf8"))
        self.assertEqual(1, str(response.content, "utf8").count(f'"amount": 6000'), str(response.content, "utf8"))
        self.assertEqual(2, str(response.content, "utf8").count(f'"withdrawal_status": "unpaid"'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"txn_fee": 0'))
        self.assertEqual(1, str(response.content, "utf8").count(f'"txn_fee": 30'))


