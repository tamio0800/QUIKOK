from django.test import TestCase, Client, RequestFactory
from .models import student_purchase_record, student_remaining_minutes_of_each_purchased_lesson_set
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
        'total_amount_of_the_sales_set': 300,
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
        'total_amount_of_the_sales_set': 300,
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
        'total_amount_of_the_sales_set': 300,
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
        'sales_set': 'no_discount',#'trial',,'30:70']
        'total_amount_of_the_sales_set': 300,
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
        # 將訂單3,4,5,6 改成已付款,要先改為付款才會長出計算剩餘時間的table
        paid_order_num = [3,4,5,6]
        order_query_list = student_purchase_record.objects.filter(id__in =paid_order_num)
        for order in order_query_list:    
            order.payment_status = 'paid'
            order.save()
        # 訂單4 再改為退款中
        order = student_purchase_record.objects.get(id=4)
        order.payment_status = 'refunding'
        order.save()
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
        self.assertEqual(student_remaining_minutes_of_each_purchased_lesson_set.objects.all().count(),len(paid_order_num))

    def test_oreder_history_response(self):
        data = {
            'userID':'2',
            'token':'1',
            'type':'1'
        }
        response = self.client.post(path='/api/account_finance/studentOrderHistory/', data=data)
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
        
    def test_student_edit_order_paid(self):
        '''
        check update payment_status改成對帳中refunding, 且有存入銀行5碼 
        '''
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
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', str(response.content))
        self.assertEqual(record.payment_status , 'refunding')
        self.assertEqual(record.part_of_bank_account_code, '11111')
    
    def test_student_edit_order_apply_refund(self):
        data = {
            'userID':'2',
            'token':'1',
            'type':'1',
            'purchase_recordID':1,
            'status_update':1,
            'user5_bank_code':11111
        }
        response = self.client.post(path='/api/account_finance/studentOrderHistory/', data=data)
        self.assertEqual(response.status_code, 200)
    def test_student_edit_order_cancel_before_paid(self):
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



        




'''
the_purchase_object = \
    student_purchase_record.objects.first()
the_purchase_object.payment_status = 'paid'
the_purchase_object.save()
# 理論上現在已經購買、付款完成了，所以 學生1應該有30min的可用時數

booking_post_data = {
    'userID': student_profile.objects.first().auth_id,  # 學生的auth_id
    'lessonID': 1,
    'bookingDateTime': f'{self.available_date_2_t1}:1,2,3,4;{self.available_date_3_t1}:1,3,4,5;'
}  # 預約 240min  >> 1234 1 345 3門課

self.client.post(
    path='/api/lesson/bookingLessons/',
    data=booking_post_data)  # 送出預約，此時學生應該有3則送出的 待確認 預約訊息
'''

