from django.shortcuts import render
import math
from account_finance.models import (student_purchase_record, 
student_remaining_minutes_of_each_purchased_lesson_set, 
student_remaining_minutes_when_request_refund_each_purchased_lesson_set)
from account_finance.email_sending import email_manager, email_for_edony
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info
from django.http import JsonResponse
from chatroom.consumers import ChatConsumer
from datetime import datetime, timedelta, timezone, date as date_function
from handy_functions import check_if_all_variables_are_true
from django.views.decorators.http import require_http_methods
from account_finance.models import student_refund, teacher_refund
from time import time
from threading import Thread


def view_email_new_order_remind(request):
    return render(request, 'send_new_order_remind.html')


email_notification = email_manager()

def storage_order(request):
    # 訂單(方案)結帳
    st = time()
    response = dict()
    try:
        student_authID = request.POST.get('userID', False)
        teacher_authID = request.POST.get('teacherID', False)
        lesson_id = request.POST.get('lessonID', False)
        lesson_set = request.POST.get('sales_set', False)
        price = request.POST.get('total_amount_of_the_sales_set', False)
        q_discount_amount = request.POST.get('q_discount', False)

        # 這兩個寫在這裡可能導致失敗(參數沒抓到)，而且檢查 None 的速度比 len() 快很多
        #teacher_queryset = teacher_profile.objects.filter(auth_id= teacher_authID)
        #lesson_queryset = lesson_info.objects.filter(id = lesson_id)
        
        if check_if_all_variables_are_true(student_authID, teacher_authID,
            lesson_id, lesson_set, price, q_discount_amount):

            teacher_obj = teacher_profile.objects.filter(auth_id=teacher_authID).first()
            lesson_obj = lesson_info.objects.filter(id=lesson_id).first()
            student_obj = student_profile.objects.get(auth_id=student_authID)

            if None not in (teacher_obj, lesson_obj):
                set_obj = lesson_sales_sets.objects.filter(
                                lesson_id=lesson_id, sales_set=lesson_set, is_open= True).first()
                if set_obj is not None:
                    # 確認前端傳來的總金額等於資料庫裡的總金額
                    if int(price) == set_obj.total_amount_of_the_sales_set:
                    # 學生欲使用Q幣折抵現金
                        #print('金額有一樣唷~')
                        if q_discount_amount != '0':
                            # 確認學生有的q幣是否有大於等於要使用的Q幣的餘額
                            student_balance = student_obj.balance
                            if student_balance >= int(q_discount_amount):
                                # 如果要買試教課程,先檢查是否已經買過了、尚未結帳
                                if lesson_set == 'trial':
                                    student_purchase_object = \
                                        student_purchase_record.objects.filter(
                                            lesson_sales_set_id = set_obj.id, 
                                            student_auth_id = student_authID
                                        ).order_by('id').first()
                                    # >0 表示已買過
                                    if student_purchase_object is not None:
                                        # 如果買過但又取消、依然可以買
                                        last_record_payment_status = student_purchase_object.payment_status
                                        if last_record_payment_status == 'unpaid_cancel':
                                            real_price = int(price) - int(q_discount_amount)
                                            # 更新學生Q幣預扣餘額
                                            # student_obj = student_profile.objects.get(auth_id=student_authID)
                                            # 預扣額度更新,不能直接覆蓋,要加上去
                                            student_obj.withholding_balance += int(q_discount_amount)
                                            student_obj.balance -= int(q_discount_amount)
                                            student_obj.save()

                                            # teacher_obj = teacher_queryset.first()
                                            # lesson_obj = lesson_queryset.first()
                                            # purchase_date = datetime.now()
                                            payment_deadline = datetime.now() + timedelta(days=6)

                                            # 建立訂單
                                            new_record = student_purchase_record.objects.create(
                                                student_auth_id= student_authID,
                                                teacher_auth_id= teacher_authID,
                                                teacher_nickname= teacher_obj.nickname,
                                                purchase_date = date_function.today(),
                                                payment_deadline = payment_deadline,
                                                lesson_id = lesson_id,
                                                lesson_title = lesson_obj.lesson_title,
                                                lesson_sales_set_id = set_obj.id,
                                                price = price,
                                                purchased_with_q_points = q_discount_amount,
                                                purchased_with_money=real_price
                                                )
                                            new_record.save()

                                            # 寄通知
                                            notification = {
                                                'studentID' :student_authID, 
                                                'teacherID':teacher_authID,
                                                'lessonID': lesson_id, 
                                                'lesson_set': lesson_set, 
                                                'total_lesson_set_price':price,
                                                'email_pattern_name':'訂課匯款提醒',
                                                'q_discount':q_discount_amount,
                                                'purchasing_price':real_price
                                                }

                                            # chatroom傳送通知
                                            #chatroom_notification = ChatConsumer()
                                            #chatroom_notification.system_msg_new_order_payment_remind(**notification)
                                            # email傳送通知
                                            # email_notification = email_manager()
                                            # email_notification.system_email_new_order_and_payment_remind(**notification)
                                            
                                            response = {'status':'success',
                                            'errCode': None,
                                            'errMsg': None,
                                            'data': new_record.id}

                                            the_thread = Thread(
                                                target=email_notification.system_email_new_order_and_payment_remind,
                                                kwargs=notification)
                                            the_thread.start()
                                            print(f"consumed time test: {time()-st}")

                                        else:
                                            response = {'status':'failed',
                                                        'errCode': 6,
                                                        'errMsg': '您已選購此堂課程的試教方案，請前往帳務中心查看或選擇其他方案',
                                                        'data': None}

                                    else: # 還沒買過, 可以買
                                        real_price = int(price) - int(q_discount_amount)
                                        # 更新學生Q幣預扣餘額
                                        # 預扣額度更新,不能直接覆蓋,要加上去
                                        student_obj.withholding_balance += int(q_discount_amount)
                                        student_obj.balance -= int(q_discount_amount)
                                        student_obj.save()

                                        payment_deadline = datetime.now() + timedelta(days=6)

                                        # 建立訂單
                                        new_record = student_purchase_record.objects.create(
                                            student_auth_id= student_authID,
                                            teacher_auth_id= teacher_authID,
                                            teacher_nickname= teacher_obj.nickname,
                                            purchase_date = date_function.today(),
                                            payment_deadline = payment_deadline,
                                            lesson_id = lesson_id,
                                            lesson_title = lesson_obj.lesson_title,
                                            lesson_sales_set_id = set_obj.id,
                                            price = price,
                                            purchased_with_q_points = q_discount_amount,
                                            purchased_with_money=real_price
                                            )
                                        new_record.save()

                                        # 寄通知
                                        notification = {
                                            'studentID' :student_authID, 
                                            'teacherID':teacher_authID,
                                            'lessonID': lesson_id, 
                                            'lesson_set': lesson_set, 
                                            'total_lesson_set_price':price,
                                            'email_pattern_name':'訂課匯款提醒',
                                            'q_discount':q_discount_amount,
                                            'purchasing_price':real_price
                                            }

                                        # chatroom傳送通知
                                        #chatroom_notification = ChatConsumer()
                                        #chatroom_notification.system_msg_new_order_payment_remind(**notification)
                                        # email傳送通知
                                        # email_notification = email_manager()
                                        # email_notification.system_email_new_order_and_payment_remind(**notification)
                                        response = {'status':'success',
                                        'errCode': None,
                                        'errMsg': None,
                                        'data': new_record.id}

                                        the_thread = Thread(
                                            target=email_notification.system_email_new_order_and_payment_remind,
                                            kwargs=notification)
                                        the_thread.start()
                                        print(f"consumed time test: {time()-st}")
                                        

                                else: # 不是選試上課就不檢查有沒有買過了,使用者愛一次買幾個都可以
                                    real_price = int(price) - int(q_discount_amount)
                                    # 更新學生Q幣預扣、帳戶餘額
                                    # 預扣額度更新,不能直接覆蓋,要加上去
                                    student_obj.withholding_balance += int(q_discount_amount)
                                    student_obj.balance -= int(q_discount_amount)
                                    student_obj.save()

                                    payment_deadline = datetime.now() + timedelta(days=6)

                                    # 建立訂單
                                    new_record = student_purchase_record.objects.create(
                                        student_auth_id= student_authID,
                                        teacher_auth_id= teacher_authID,
                                        teacher_nickname= teacher_obj.nickname,
                                        purchase_date = date_function.today(),
                                        payment_deadline = payment_deadline,
                                        lesson_id = lesson_id,
                                        lesson_title = lesson_obj.lesson_title,
                                        lesson_sales_set_id = set_obj.id,
                                        price = price,
                                        purchased_with_q_points = q_discount_amount,
                                        purchased_with_money=real_price
                                        )
                                    new_record.save()

                                    # 寄通知
                                    notification = {
                                        'studentID' :student_authID, 
                                        'teacherID':teacher_authID,
                                        'lessonID': lesson_id, 
                                        'lesson_set': lesson_set, 
                                        'total_lesson_set_price':price,
                                        'email_pattern_name':'訂課匯款提醒',
                                        'q_discount':q_discount_amount,
                                        'purchasing_price':real_price
                                        }

                                    # chatroom傳送通知
                                    #chatroom_notification = ChatConsumer()
                                    #chatroom_notification.system_msg_new_order_payment_remind(**notification)
                                    # email傳送通知
                                    #email_notification = email_manager()
                                    #email_notification.system_email_new_order_and_payment_remind(**notification)
                                    response = {'status':'success',
                                    'errCode': None,
                                    'errMsg': None,
                                    'data': new_record.id}

                                    the_thread = Thread(
                                        target=email_notification.system_email_new_order_and_payment_remind,
                                        kwargs=notification)
                                    the_thread.start()
                                    print(f"consumed time test: {time()-st}")

                            else:
                                response = {'status':'failed',
                                    'errCode': 5,
                                    'errMsg': '您的Q幣餘額不足，您只能抵用自己帳戶Q幣的餘額。\
                                                如有疑問可連絡客服',
                                    'data': None}
                        else: # 沒有使用q幣
                            # 如果要買試教課程,先檢查是否已經買過了、尚未結帳
                            if lesson_set == 'trial':
                                #check_trial_query_exist = student_purchase_record.objects.filter(
                                #                            lesson_sales_set_id = set_obj.id, 
                                #                            student_auth_id = student_authID).order_by('-id')

                                student_purchase_record_obj = \
                                    student_purchase_record.objects.filter(
                                        lesson_sales_set_id = set_obj.id, 
                                        student_auth_id = student_authID
                                    ).order_by('id').last()

                                # >0 表示已買過
                                # 一樣，len很耗運算資源，既然query默認是用id排序，則可以使用
                                if student_purchase_record_obj is not None:
                                    last_record_payment_status = student_purchase_record_obj.payment_status
                                    # 但如果買過又取消,還是可以買
                                    if last_record_payment_status == 'unpaid_cancel':
                                        real_price = int(price)
                                        # teacher_obj = teacher_queryset.first()
                                        # lesson_obj = lesson_queryset.first()
                                        # purchase_date = datetime.now()
                                        payment_deadline = datetime.now() + timedelta(days=6)
                                        # 建立訂單
                                        new_record = student_purchase_record.objects.create(
                                            student_auth_id= student_authID,
                                            teacher_auth_id= teacher_authID,
                                            teacher_nickname= teacher_obj.nickname,
                                            purchase_date = date_function.today(),
                                            payment_deadline = payment_deadline,
                                            lesson_id = lesson_id,
                                            lesson_title = lesson_obj.lesson_title,
                                            lesson_sales_set_id = set_obj.id,
                                            price = price,
                                            purchased_with_q_points = q_discount_amount,
                                            purchased_with_money=real_price
                                            )
                                        new_record.save()

                                        # 寄通知
                                        notification = {
                                            'studentID' :student_authID, 
                                            'teacherID':teacher_authID,
                                            'lessonID': lesson_id, 
                                            'lesson_set': lesson_set, 
                                            'total_lesson_set_price':price,
                                            'email_pattern_name':'訂課匯款提醒',
                                            'q_discount':q_discount_amount,
                                            'purchasing_price':real_price
                                            }

                                        # chatroom傳送通知
                                        #chatroom_notification = ChatConsumer()
                                        #chatroom_notification.system_msg_new_order_payment_remind(**notification)
                                        # email傳送通知
                                        #email_notification = email_manager()
                                        #email_notification.system_email_new_order_and_payment_remind(
                                        #                                                    **notification)
                                        #email_notification_with_thread = EMAIL_MANAGER_WITH_THREAD(**notification)
                                        #email_notification_with_thread.start()
                                        #print(f"consumed time: {time()-st}")

                                        response = {'status':'success',
                                        'errCode': None,
                                        'errMsg': None,
                                        'data': new_record.id}

                                        the_thread = Thread(
                                            target=email_notification.system_email_new_order_and_payment_remind,
                                            kwargs=notification)
                                        the_thread.start()
                                        print(f"consumed time test: {time()-st}")

                                    else: #有買過或正在買的試教課程
                                        response = {'status':'failed',
                                                    'errCode': 6,
                                                    'errMsg': '您已選購此堂課程的試教方案，請前往帳務中心查看或選擇其他方案',
                                                    'data': None}

                                else: # 沒買過,可以買試教
                                    real_price = int(price)
                                    # teacher_obj = teacher_queryset.first()
                                    # lesson_obj = lesson_queryset.first()
                                    # purchase_date = datetime.now()
                                    payment_deadline = datetime.now() + timedelta(days=6)

                                    # 建立訂單
                                    new_record = student_purchase_record.objects.create(
                                        student_auth_id= student_authID,
                                        teacher_auth_id= teacher_authID,
                                        teacher_nickname= teacher_obj.nickname,
                                        purchase_date = date_function.today(),
                                        payment_deadline = payment_deadline,
                                        lesson_id = lesson_id,
                                        lesson_title = lesson_obj.lesson_title,
                                        lesson_sales_set_id = set_obj.id,
                                        price = price,
                                        purchased_with_q_points = q_discount_amount,
                                        purchased_with_money=real_price
                                        )
                                    new_record.save()

                                    # 寄通知
                                    notification = {
                                        'studentID' :student_authID, 
                                        'teacherID':teacher_authID,
                                        'lessonID': lesson_id, 
                                        'lesson_set': lesson_set, 
                                        'total_lesson_set_price':price,
                                        'email_pattern_name':'訂課匯款提醒',
                                        'q_discount':q_discount_amount,
                                        'purchasing_price':real_price
                                        }

                                    # chatroom傳送通知
                                    #chatroom_notification = ChatConsumer()
                                    #chatroom_notification.system_msg_new_order_payment_remind(**notification)
                                    # email傳送通知
                                    #email_notification_with_thread = EMAIL_MANAGER_WITH_THREAD(**notification)
                                    #email_notification_with_thread.start()
                                    #print(f"consumed time: {time()-st}")
                                    #email_notification = email_manager()
                                    #email_notification.system_email_new_order_and_payment_remind(**notification)

                                    response = {'status':'success',
                                    'errCode': None,
                                    'errMsg': None,
                                    'data': new_record.id}

                                    the_thread = Thread(
                                        target=email_notification.system_email_new_order_and_payment_remind,
                                        kwargs=notification)
                                    the_thread.start()
                                    print(f"consumed time test: {time()-st}")

                            else: #不是選試上課就不檢查有沒有買過了,使用者愛一次買幾個都可以
                                real_price = int(price)
                                # eacher_obj = teacher_queryset.first()
                                # lesson_obj = lesson_queryset.first()
                                # purchase_date = datetime.now()
                                payment_deadline = datetime.now() + timedelta(days=6)

                                # 建立訂單
                                new_record = student_purchase_record.objects.create(
                                    student_auth_id= student_authID,
                                    teacher_auth_id= teacher_authID,
                                    teacher_nickname= teacher_obj.nickname,
                                    purchase_date = date_function.today(),
                                    payment_deadline = payment_deadline,
                                    lesson_id = lesson_id,
                                    lesson_title = lesson_obj.lesson_title,
                                    lesson_sales_set_id = set_obj.id,
                                    price = price,
                                    purchased_with_q_points = q_discount_amount,
                                    purchased_with_money=real_price
                                    )
                                new_record.save()

                                # 寄通知
                                notification = {
                                    'studentID' :student_authID, 
                                    'teacherID':teacher_authID,
                                    'lessonID': lesson_id, 
                                    'lesson_set': lesson_set, 
                                    'total_lesson_set_price':price,
                                    'email_pattern_name':'訂課匯款提醒',
                                    'q_discount':q_discount_amount,
                                    'purchasing_price':real_price
                                    }

                                # chatroom傳送通知
                                #chatroom_notification = ChatConsumer()
                                #chatroom_notification.system_msg_new_order_payment_remind(**notification)
                                # email傳送通知
                                
                                #email_notification.system_email_new_order_and_payment_remind(**notification)
                    
                                response = {'status':'success',
                                'errCode': None,
                                'errMsg': None,
                                'data': new_record.id}

                                the_thread = Thread(
                                    target=email_notification.system_email_new_order_and_payment_remind,
                                    kwargs=notification)
                                the_thread.start()
                                print(f"consumed time test: {time()-st}")

                                return JsonResponse(response)
                    else:# 正常情況下前端傳來的金額要與資料庫一致
                        response = {'status':'failed',
                        'errCode': 4,
                        'errMsg': '課程金額有問題，請稍後再試，如狀況持續可連絡客服',
                        'data': set_obj.total_amount_of_the_sales_set}
                else:
                    response = {'status':'failed',
                    'errCode': 0,
                    'errMsg': '系統找不到該門課程方案，請稍後再試，如狀況持續可連絡客服',
                    'data': None}
            else:
                response = {'status':'failed',
                'errCode': 1,
                'errMsg': '系統找不到老師或該門課程，請稍後再試，如狀況持續可連絡客服',
                'data': None}
        else:
            response = {'status':'failed',
            'errCode': 2,
            'errMsg': '資料庫有問題，請稍後再試',
            'data': None}

        return JsonResponse(response)

    
    except Exception as e:
        print(f'storage_order Exception {e}')
        response = {'status':'failed',
        'errCode': 3,
        'errMsg': '資料庫有問題，請稍後再試',
        'data': None}
        return JsonResponse(response)

#回傳訂單紀錄api, 我的存摺頁
def student_order_history(request):
    try:
        student_authID = request.POST.get('userID', False)
        token_from_user_raw = request.headers.get('Authorization', False)
        if token_from_user_raw is not False:
            token = token_from_user_raw.split(' ')[1]
        else:
            token = ''
        user_type = request.POST.get('type', False)
        if check_if_all_variables_are_true(student_authID, user_type):
            data = []
            record_history = {}
            remittance_info = {
                    'bank_code': '088',
                    'bank_name': '國泰世華銀行',
                    'bank_branches': '板橋分行',
                    'bank_account':'012345-411153',
                    'bank_account_name': '豆沙科技股份有限公司'}
            for record in student_purchase_record.objects.filter(student_auth_id=student_authID):
                set_name = lesson_sales_sets.objects.filter(id=record.lesson_sales_set_id).first()
                
                # 所有尚未確認時間計算用
                if set_name.sales_set == 'trial':
                    total_time = 30
                # 試教總時數等於半小時
                #    record_set_name = '試教'
                elif set_name.sales_set == 'no_discount':
                    total_time = 60
                #買單堂課的時數為一個小時((嚴格來說是兩堂課
                #    record_set_name = '單堂'
                else:
                    lesson_time = set_name.sales_set.split(':')[0]
                    total_time = int(lesson_time)*60 # 小時轉成分鐘
                #    lesson_discount = set_name.sales_set.split[1]
                #    if '0' in lesson_discount: # 70 折-> 7折
                #        lesson_discount = set_discount.strip('0')
                #    record_set_name = f'{lesson_time}小時{lesson_discount}折'
                
                # 如果這筆訂單還沒從reconciliation改成paid, 剩餘時數的table也就還沒長出來
                # 所以必須把分付款狀態來處理
                if record.payment_status in ['paid','refunded', 'cancel_after_paid']:
                    
                    remain_time_info = student_remaining_minutes_of_each_purchased_lesson_set.objects.get(student_purchase_record_id=record.id)
                    total_non_confirmed_minutes = total_time - remain_time_info.confirmed_consumed_minutes
                    available_remaining_minutes = remain_time_info.available_remaining_minutes
                    # 回傳退款金額
                    if record.payment_status in ['refunded', 'cancel_after_paid']:
                        refunded_price = student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.get(
                            student_purchase_record_id=record.id).available_minutes_turn_into_q_points
                    else:
                        refunded_price = ''
                else:
                    refunded_price = ''
                    available_remaining_minutes = ''
                    total_non_confirmed_minutes = ''
                
                # 將日期轉換為給前端的格式
                purchase_date = record.purchase_date
                date_format_change = purchase_date.strftime('%Y-%m-%d')
                
                #print(available_remaining_minutes)
                record_history = {
                'purchase_recordID':record.id,
                'purchase_status':record.payment_status,
                'refunded_price':refunded_price,
                'purchase_date':date_format_change,
                'teacher_authID':record.teacher_auth_id,
                'teacher_nickname': record.teacher_nickname,
                'lesson_name': record.lesson_title,
                'lessonID': record.lesson_id,
                'lesson_sales_set': set_name.sales_set, 
                'purchased_with_money':record.purchased_with_money,
                'available_remaining_minutes': available_remaining_minutes,
                'total_non_confirmed_minutes': total_non_confirmed_minutes} #全部時數減掉已confirm完課的時數,主要是給老師看的
                #'付款末五碼': record.part_of_bank_account_code} # 後五碼

                record_history['edony_bank_info'] = remittance_info
                data.append(record_history)
            #print(data)

            response = {'status':'success',
                        'errCode': None,
                        'errMsg': None,
                        'data': data}
        else:
            response = {'status':'failed',
            'errCode': 0,
            'errMsg': '系統沒有收到資料，請重新整理，如狀況持續可連絡客服',
            'data': []}

    except Exception as e:
        print(f'account_finance/views, student_order_history storage_order Exception {e}')
        response = {'status':'failed',
        'errCode': 1,
        'errMsg': '資料庫有問題，請稍後再試',
        'data': []}
    return JsonResponse(response)


# 編輯訂單狀態api, 包含取消訂單
def student_edit_order(request):
    try:
        student_authID = request.POST.get('userID', False)
        token_from_user_raw = request.headers.get('Authorization', False)
        if token_from_user_raw is not False:
            token = token_from_user_raw.split(' ')[1]
        else:
            token = ''
        user_type = request.POST.get('type', False)
        purchase_recordID = request.POST.get('purchase_recordID', False)
        status_update = request.POST.get('status_update', False)
        # 0-付款完成/1-申請退款/2-申請取消
        user5_bank_code = request.POST.get('part_of_bank_account_code', False)

        if check_if_all_variables_are_true(student_authID, user_type,
                            purchase_recordID, status_update, user5_bank_code):
            # 首先查詢訂單狀態
            record = student_purchase_record.objects.get(id = purchase_recordID)
            student_obj = student_profile.objects.filter(auth_id=student_authID).first()
            if student_obj is None: # 正常不會是none
                response = {'status':'failed',
                    'errCode': 7,
                    'errMsg': '找不到學生ID，資料庫有問題，請稍後再試',
                    'data': None}
            else:
                # 訂單已付款,理論上只有'paid'申請退款或取消兩種
                # 萬一客人先在訂單這邊取消 但還有尚未進行的預約沒取消, 這種情況暫時無法處理
                if record.payment_status == 'paid': #'refunding','refunded', 'cancel_after_paid'
                    if status_update == '1': # 申請退款
                        lesson_set = lesson_sales_sets.objects.get(id = record.lesson_sales_set_id)
                        remain_time = student_remaining_minutes_of_each_purchased_lesson_set.objects.get(student_purchase_record_id=record.id)
                        # 換算q幣,先查詢是哪種方案
                        if lesson_set.sales_set == 'trial':
                            if remain_time.available_remaining_minutes > 0:
                                # 訂單跟剩餘時數都改為已退費
                                record.payment_status = 'refunded'
                                record.save()
                                remain_time.is_refunded = 1
                                remain_time.save()
                                # 退試課的全額
                                refund_price =  lesson_set.total_amount_of_the_sales_set
                                # 建立退費紀錄
                                student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.create(
                                    student_purchase_record_id= record.id,
                                    purchased_lesson_sales_sets_id=lesson_set.id,
                                    snapshot_available_remaining_minutes = remain_time.available_remaining_minutes,
                                    snapshot_withholding_minutes=remain_time.withholding_minutes,
                                    available_minutes_turn_into_q_points= refund_price,
                                ).save()
                                
                                # 增加q幣餘額
                                #student_obj = student_profile.objects.get(auth_id=student_authID)
                                student_obj.balance = student_obj.balance + refund_price
                                student_obj.save()
                                response = {'status':'success',
                                    'errCode': None,
                                    'errMsg': None,
                                    'data': None}
                            else:
                                response = {'status':'failed',
                                'errCode': 4,
                                'errMsg': '您的訂單已無剩餘時數可退，如有疑慮請聯絡客服協助您處理，謝謝',
                                'data': None}

                            # no_discount 單堂課退款
                        elif lesson_set.sales_set == 'no_discount':    
                            if remain_time.available_remaining_minutes > 0:
                                # 假設剩10分鐘,表示已用60-10= 50分鐘
                                time_had_used = 60 - remain_time.available_remaining_minutes
                                # 已用時間價值 = 已用分鐘*(假設1小時60元,每分鐘 = 60/60元)
                                price_had_used = time_had_used * (lesson_set.price_per_hour/60)
                                price_had_used = math.ceil(price_had_used) # 無條件進位到整數
                                # 付出總金額 - 已用時間價值
                                refund_price =  record.purchased_with_money - price_had_used
                                
                                if refund_price > 0: # 理論上都會大於0
                                    # 建立退費紀錄
                                    student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.create(
                                        student_purchase_record_id= record.id,
                                        purchased_lesson_sales_sets_id=lesson_set.id,
                                        snapshot_available_remaining_minutes = remain_time.available_remaining_minutes,
                                        snapshot_withholding_minutes=remain_time.withholding_minutes,
                                        available_minutes_turn_into_q_points= refund_price,
                                    ).save()
                                    # 增加q幣餘額
                                    #student_obj = student_profile.objects.get(auth_id=student_authID)
                                    student_obj.balance = student_obj.balance + refund_price
                                    student_obj.save()
                                    # 狀態改為已匯款
                                    record.payment_status = 'refunded'
                                    record.save()
                                    # 剩餘時數表格改為已退款
                                    remain_time.is_refunded = 1
                                    remain_time.save()

                                    response = {'status':'success',
                                        'errCode': None,
                                        'errMsg': None,
                                        'data': None}
                                else:
                                    response = {'status':'failed',
                                    'errCode': 4,
                                    'errMsg': '您的訂單已無剩餘時數可退，如有疑慮請聯絡客服協助您處理，謝謝',
                                    'data': None}
                            else:
                                response = {'status':'failed',
                                    'errCode': 4,
                                    'errMsg': '您的訂單已無剩餘時數可退，如有疑慮請聯絡客服協助您處理，謝謝',
                                    'data': None}
                            

                        # 多堂優惠要退費的情況
                        else:
                            if remain_time.available_remaining_minutes > 0:
                                total_set_time = int(lesson_set.sales_set.split(':')[0])*60 # 小時轉分鐘
                                #set_dicount = int(lesson_set.sales_set.split(':')[1])/100 # 折數
                                # 假設剩10分鐘,表示已用60-10= 50分鐘
                                time_had_used = total_set_time - remain_time.available_remaining_minutes
                                # 已用時間價值 = 已用分鐘*每分鐘價值(假設1小時60元,每分鐘 = 60/60元)
                                price_had_used = time_had_used * (lesson_set.price_per_hour/60)
                                price_had_used = math.ceil(price_had_used) # 無條件進位到整數
                                # 退款金額= 付出總金額 - 已用時間價值
                                refund_price =  record.purchased_with_money - price_had_used
                                
                                if refund_price > 0: # 有可能會小於0
                                    # 建立退費紀錄
                                    student_remaining_minutes_when_request_refund_each_purchased_lesson_set.objects.create(
                                        student_purchase_record_id= record.id,
                                        purchased_lesson_sales_sets_id=lesson_set.id,
                                        snapshot_available_remaining_minutes = remain_time.available_remaining_minutes,
                                        snapshot_withholding_minutes=remain_time.withholding_minutes,
                                        available_minutes_turn_into_q_points= refund_price,
                                    ).save()
                                    # 增加q幣餘額
                                    #student_obj = student_profile.objects.get(auth_id=student_authID)
                                    student_obj.balance = student_obj.balance + refund_price
                                    student_obj.save()
                                    # 狀態改為已匯款
                                    record.payment_status = 'refunded'
                                    record.save()
                                    # 剩餘時數表格改為已退款
                                    remain_time.is_refunded = 1
                                    remain_time.save()
                                    
                                    response = {'status':'success',
                                        'errCode': None,
                                        'errMsg': None,
                                        'data': None}
                                else:
                                    response = {'status':'failed',
                                    'errCode': 5,
                                    'errMsg': '您完課的時數需照單堂課原價計算，沒有多堂課優惠，經計算您所剩的時間若轉換回原價已超過本訂單匯款金額\
                                    ，恕無法退費。如有疑慮請聯絡客服協助您處理，謝謝',
                                    'data': None}
                            
                            else:
                                response = {'status':'failed',
                                    'errCode': 4,
                                    'errMsg': '您的訂單已無剩餘時數可退，如有疑慮請聯絡客服協助您處理，謝謝',
                                    'data': None}

                # 訂單尚未付款
                elif record.payment_status == 'unpaid':
                    if status_update == '0': # 學生已付款,接著我們要對帳
                        record.payment_status = 'reconciliation'
                        record.part_of_bank_account_code = user5_bank_code
                        record.save()
                        email_to_edony = email_for_edony()
                        email_to_edony.send_email_reconciliation_reminder(student_authID=student_authID,
                        user5_bank_code =user5_bank_code, total_price = record.purchased_with_money)
                        response = {'status':'success',
                                    'errCode': None,
                                    'errMsg': None,
                                    'data': None}
                                    
                    elif status_update == '2': 
                        # 申請取消 如果這筆訂單沒有用q幣折抵不用動作,如果有用q幣,
                        # 要 1.把預扣金額扣掉q的數字,2. balance(餘額)加上q的數字
                        if record.purchased_with_q_points > 0:
                        # 訂單有用q幣折抵
                            student_obj.balance += record.purchased_with_q_points
                            student_obj.withholding_balance -= record.purchased_with_q_points
                            student_obj.save()
                        else: # 訂單沒有用q幣折抵
                            pass
                        
                        record.payment_status = 'unpaid_cancel'
                        record.save()
                        response = {'status':'success',
                                    'errCode': None,
                                    'errMsg': None,
                                    'data': None}
                    else:
                        response = {'status':'failed',
                        'errCode': 3,
                        'errMsg': '您的訂單有問題，請聯絡客服協助您處理，謝謝！',
                        'data': None}

                else: # 不是已付款或未付款不能動作
                    response = {'status':'failed',
                    'errCode': 6,
                    'errMsg': '您的訂單狀態有問題，請聯絡客服協助您處理，謝謝！',
                    'data': None}
                    

        else:
            print(student_authID, token,user_type,purchase_recordID,status_update, user5_bank_code)
            response = {'status':'failed',
            'errCode': 2,
            'errMsg': '資料庫有問題，請稍後再試',
            'data': None}
        return JsonResponse(response)
        
    except Exception as e:
        print(f'storage_order Exception {e}')
        response = {'status':'failed',
        'errCode': 1,
        'errMsg': '資料庫有問題，請稍後再試',
        'data': None}
    
        return JsonResponse(response)

#def confirm_lesson_order_payment_page(request):
#    all_unconfirm_users = student_purchase_record.objects.filter(payment_status='unpaid')
#    return render(request, 'confirm_order_payment.html',
#    {'all_unconfirm_users':all_unconfirm_users})


@require_http_methods(['POST'])
def get_lesson_sales_history(request):
    '''
    回傳老師的課程方案販賣紀錄，目前只做老師
    收取資料: {
        userID: teacher's auth_id,
        type: "teacher" or "student"
    }
    回傳資料:{
            status: “success“ / “failed“ 
            errCode: None 
            errMsg: None
            data:[
                    {
                    售課紀錄ID: 0
                    狀態: 0-進行中/1-已結案/2-已退費  >> "on_going"、"finished"、"refunded"
                    日期: 2020-01-01
                    學生暱稱: XX
                    學生ID: 0
                    課程名稱: XXXXX
                    lessonID: 0
                    購買方案: 10:90
                    金額: 000
                    剩餘可預約時間(分鐘): 135,
                    剩餘未完課時間(分鐘): 135
                    is_selling: Boolean   (該方案是否仍然在架上販賣)
                    }...
            ]
    }'''
    response = dict()
    teacher_auth_id = request.POST.get('userID', False)
    user_type = request.POST.get('type', False)
    
    if check_if_all_variables_are_true(teacher_auth_id, user_type):
        # 資料傳輸成功
        the_teacher_object = teacher_profile.objects.filter(auth_id=teacher_auth_id).first()
        if the_teacher_object is not None:
            # 這名老師確實存在
            # 來把跟他有關的已購買的購買紀錄都列出來吧，並且把最新的購買日期放在最上面 >> time desc.
            his_related_purchased_record_queryset = \
                student_purchase_record.objects.filter(
                    teacher_auth_id = teacher_auth_id,
                    payment_status__in = ['paid', 'refunding', 'refund', 'cancel']
                ).order_by('-purchase_date')
            
            if (his_related_purchased_record_queryset.count()):
                response['data'] = list()
                # 代表這個老師有與他相關的購買紀錄
                # 接著儲存相關的資料
                for each_his_related_purchased_record in his_related_purchased_record_queryset:
                    correspondent_student_remaining_minutes_object = \
                        student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
                            student_purchase_record_id = each_his_related_purchased_record.id
                        ).first() # 上面這段是為了求得目前這個方案的狀態是：已經成功結束了、進行中、或是已退費之類的

                    # 因為一門課程的一個方案，可能被購買了許多次，所以需要進行這個環節
                    if correspondent_student_remaining_minutes_object is not None:
                        # 如果是None的話代表沒有進到paid，這一步，因此不需要做紀錄

                        if correspondent_student_remaining_minutes_object.is_refunded == True:
                            purchased_lesson_sales_set_status = 'refunded'
                        elif correspondent_student_remaining_minutes_object.available_remaining_minutes + \
                            correspondent_student_remaining_minutes_object.withholding_minutes == 0:
                            # 可預約時間 跟 預扣時間 都為零，代表已經消耗殆盡了 >> 已結束
                            purchased_lesson_sales_set_status = 'finished'
                        else:
                            # 代表課程進行中
                            purchased_lesson_sales_set_status = 'on_going'
                    
                        created_date = str(correspondent_student_remaining_minutes_object.created_time).split()[0]
                        # 完成結帳，產生對應tables時的那一天
                        student_auth_id = correspondent_student_remaining_minutes_object.student_auth_id
                        student_nickname = student_profile.objects.get(auth_id=student_auth_id).nickname
                        lesson_title = each_his_related_purchased_record.lesson_title
                        lesson_id = each_his_related_purchased_record.lesson_id
                        
                        lesson_sales_set_object = \
                            lesson_sales_sets.objects.get(id=each_his_related_purchased_record.lesson_sales_set_id)
                        
                        lesson_sales_set = lesson_sales_set_object.sales_set
                        total_amount = each_his_related_purchased_record.price
                        available_remaining_minutes = correspondent_student_remaining_minutes_object.available_remaining_minutes
                        total_non_confirmed_minutes = \
                            available_remaining_minutes + correspondent_student_remaining_minutes_object.withholding_minutes
                        is_selling = lesson_sales_set_object.is_open

                        response['data'].append(
                            {
                                'purchased_record_id': each_his_related_purchased_record.id,
                                'purchased_lesson_sales_set_status': purchased_lesson_sales_set_status,
                                'created_date': created_date,
                                'student_nickname': student_nickname,
                                'student_auth_id': student_auth_id,
                                'lesson_title': lesson_title,
                                'lessonID': lesson_id,
                                'lesson_sales_set': lesson_sales_set,
                                'total_amount': total_amount,
                                'available_remaining_minutes': available_remaining_minutes,
                                'total_non_confirmed_minutes': total_non_confirmed_minutes,
                                'is_selling': is_selling
                            }
                        )

                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
            else:
                # 這名老師並沒有任何與之相關的購買紀錄
                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
                response['data'] = list()

        else:
            # 這名老師並不存在
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
            response['data'] = None
    else:
        # 傳輸有問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)


@require_http_methods(['POST'])
def withdraw_q_points(request):
    '''
    這個api用來收取 老師或是學生 要將 Q幣 轉成新台幣匯出的訊息
    收取資料: {
        userID: teacher/student 's auth_id,
        type: "teacher" or "student"
        bank_code: 808 (銀行代碼)
        bank_name: 玉山銀行 (銀行名稱(選填))
        bank_account_code: 00000000000000  (銀行帳號)
        action: 純編輯 (only_editting)、編輯後請款 (withdrawal_after_editting)
        amount: 如果是「編輯後請款」的話，預計轉出的金額
    }
    回傳資料: {
            status: "success" / "failed" 
            errCode: None 
            errMsg: None
            data: None
    }'''
    response = dict()
    user_type = request.POST.get('type', False)
    
    bank_code = request.POST.get('bank_code', False)
    bank_name = request.POST.get('bank_name', False)
    bank_account_code = request.POST.get('bank_account_code', False)
    action = request.POST.get('action', False)

    if check_if_all_variables_are_true(user_type, bank_code, bank_name,
        bank_account_code, action):
        # 確實有收到除了 userID 以外的資料
        
            

        if user_type == 'teacher':
            # 老師用戶
            teacher_auth_id = request.POST.get('userID', False)
            # 先確認該用戶是否存在，以及，如果存在的話，確認他的動作是編輯或是提款
            teacher_object = teacher_profile.objects.filter(auth_id=teacher_auth_id).first()
            if teacher_object is None:
                # 該老師用戶不存在
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                response['data'] = None
            else:
                # 接著確認如果是提款的話，檢查一下Q幣夠不夠
                if action == 'withdrawal_after_editting':
                    withdrawal_amount = int(request.POST.get('amount', False))
                    # 是提款
                    if not check_if_all_variables_are_true(withdrawal_amount):
                        # 沒有填寫提款資訊
                        response['status'] = 'failed'
                        response['errCode'] = '5'
                        response['errMsg'] = '不好意思，請您要填寫匯款金額唷，謝謝您。'
                        response['data'] = None
                    else:
                        # 確認一下距離上次提款日期是否為一個月(30d)內，是的話要收手續費，反之不用
                        if teacher_refund.objects.filter(teacher_auth_id=teacher_auth_id).last() is None:
                            within_a_month = False
                        else:
                            within_a_month = \
                                (datetime.now() - teacher_refund.objects.filter(teacher_auth_id=teacher_auth_id).last().created_time).days < 31
                        txn_fee = 30 if within_a_month else 0
                        # 帳戶餘額必須 >= 手續費加上要提領的金額
                        if teacher_object.balance >= withdrawal_amount + txn_fee:
                            # Q幣足夠         
                            the_new_record = teacher_refund.objects.create(
                                teacher_auth_id = teacher_auth_id,
                                snapshot_balance = teacher_object.balance,
                                txn_fee = txn_fee,
                                refund_amount = withdrawal_amount,
                                bank_account_code = bank_account_code,
                                bank_name = bank_name,
                                bank_code = bank_code
                            )
                            the_new_record.save()
                            # 然後將user profile 的 balance 移到 withholding_balance
                            teacher_object.withholding_balance += (withdrawal_amount + txn_fee)
                            teacher_object.balance -= (withdrawal_amount + txn_fee)
                            teacher_object.save()
                            response['status'] = 'success'
                            response['errCode'] = None
                            response['errMsg'] = None
                            response['data'] = the_new_record.id
                        else:
                            # 老師要提領的Q幣不足
                            response['status'] = 'failed'
                            response['errCode'] = '3'
                            response['errMsg'] = '不好意思，您的Q幣餘額不足以進行這筆交易，如果有任何疑問請隨時向我們反應，謝謝您> <'
                            response['data'] = None
                else:
                    # 是純粹編輯，將銀行資訊寫入個人資訊中
                    teacher_object.bank_account_code = bank_account_code
                    teacher_object.bank_name = bank_name
                    teacher_object.bank_code = bank_code
                    teacher_object.save()
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                    response['data'] = None

        else:
            # 其他的一律先視為學生，反正找不到該用戶一樣會報錯
            student_auth_id = request.POST.get('userID', False)
            # 先確認該用戶是否存在，以及，如果存在的話，確認他的動作是編輯或是提款
            student_object = student_profile.objects.filter(auth_id=student_auth_id).first()
            if student_object is None:
                # 該學生用戶不存在
                response['status'] = 'failed'
                response['errCode'] = '2'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                response['data'] = None
            else:
                # 接著確認如果是提款的話，檢查一下Q幣夠不夠
                if action == 'withdrawal_after_editting':
                    withdrawal_amount = int(request.POST.get('amount', False))
                    # 是提款
                    if not check_if_all_variables_are_true(withdrawal_amount):
                        # 沒有填寫提款資訊
                        response['status'] = 'failed'
                        response['errCode'] = '6'
                        response['errMsg'] = '不好意思，請您要填寫匯款金額唷，謝謝您。'
                        response['data'] = None
                    else:
                        # 確認一下距離上次提款日期是否為一個月(30d)內，是的話要收手續費，反之不用
                        if student_refund.objects.filter(student_auth_id=student_auth_id).last() is None:
                            within_a_month = False
                        else:
                            within_a_month = \
                                (datetime.now() - student_refund.objects.filter(student_auth_id=student_auth_id).last().created_time).days < 31  
                        txn_fee = 30 if within_a_month else 0
                        if student_object.balance >= (withdrawal_amount + txn_fee):
                            # Q幣足夠
                            
                            the_new_record = student_refund.objects.create(
                                student_auth_id = student_auth_id,
                                snapshot_balance = student_object.balance,
                                txn_fee = txn_fee,
                                refund_amount = withdrawal_amount,
                                bank_account_code = bank_account_code,
                                bank_name = bank_name,
                                bank_code = bank_code
                            )
                            the_new_record.save()
                            # 然後將user profile 的 balance 移到 withholding_balance
                            student_object.withholding_balance += (withdrawal_amount + txn_fee)
                            student_object.balance -= (withdrawal_amount + txn_fee)
                            student_object.save()
                            response['status'] = 'success'
                            response['errCode'] = None
                            response['errMsg'] = None
                            response['data'] = the_new_record.id

                        else:
                            # 學生要提領的Q幣不足
                            response['status'] = 'failed'
                            response['errCode'] = '4'
                            response['errMsg'] = '不好意思，您的Q幣餘額不足以進行這筆交易，如果有任何疑問請隨時向我們反應，謝謝您> <'
                            response['data'] = None
                else:
                    # 是純粹編輯，將銀行資訊寫入個人資訊中
                    student_object.bank_account_code = bank_account_code
                    student_object.bank_name = bank_name
                    student_object.bank_code = bank_code
                    student_object.save()
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                    response['data'] = None
    else:
        # 傳輸有問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None
    
    return JsonResponse(response)


@require_http_methods(['POST'])
def get_q_points_wtihdrawal_history(request):
    '''
    這支API用來取得用戶的提領Q幣歷史資訊
    收取資料: {
        token
        userID: teacher/student 's auth_id,
        type: "teacher" or "student"
    }
    回傳資料: {
            status: "success" / "failed" 
            errCode: None 
            errMsg: None
            data: {
                withdrawal_id    請款紀錄ID: 0
                withdrawal_status   狀態
                            unpaid    付款作業中 
                            paid      已付款
                application_date  申請日期: 2020-01-01
                bank_code  銀行代碼: 808
                bank_name  銀行名稱: 玉山銀行
                bank_account_code  銀行帳號
                amount  轉出金額: 000
                txn_fee 手續費
            }
    }'''
    response = dict()
    user_type = request.POST.get('type', False)
    if check_if_all_variables_are_true(user_type):
        if user_type == 'teacher':
            # 用戶是老師
            teacher_auth_id = request.POST.get('userID', False)
            teacher_object = teacher_profile.objects.filter(auth_id=teacher_auth_id).first()

            if teacher_object is None:
                # 用戶不存在
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                response['data'] = None
            else:
                # 將歷史請款資訊從新到舊返回
                teacher_refund_queryset = \
                    teacher_refund.objects.filter(teacher_auth_id=teacher_auth_id).order_by('-created_time')
                if teacher_refund_queryset.count() == 0:
                    # 沒有歷史紀錄
                    response['data'] = list()
                else:
                    # 有歷史紀錄
                    response['data'] = list()
                    for each_teacher_refund_object in teacher_refund_queryset:
                        response['data'].append(
                            {
                                'withdrawal_id': each_teacher_refund_object.id,
                                'withdrawal_status': each_teacher_refund_object.refund_status,
                                'application_date': str(each_teacher_refund_object.created_time).split()[0],
                                'bank_code': each_teacher_refund_object.bank_code,
                                'bank_name': each_teacher_refund_object.bank_name,
                                'bank_account_code': each_teacher_refund_object.bank_account_code,
                                'amount': each_teacher_refund_object.refund_amount,
                                'txn_fee': each_teacher_refund_object.txn_fee,
                            }
                        )
                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
        else:
            # 用戶是學生
            student_auth_id = request.POST.get('userID', False)
            student_object = student_profile.objects.filter(auth_id=student_auth_id).first()

            if student_object is None:
                # 用戶不存在
                response['status'] = 'failed'
                response['errCode'] = '2'
                response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
                response['data'] = None
            else:
                # 將歷史請款資訊從新到舊返回
                student_refund_queryset = \
                    student_refund.objects.filter(student_auth_id=student_auth_id).order_by('-created_time')
                if student_refund_queryset.count() == 0:
                    # 沒有歷史紀錄
                    response['data'] = list()
                else:
                    # 有歷史紀錄
                    response['data'] = list()
                    for each_student_refund_object in student_refund_queryset:
                        response['data'].append(
                            {
                                'withdrawal_id': each_student_refund_object.id,
                                'withdrawal_status': each_student_refund_object.refund_status,
                                'application_date': str(each_student_refund_object.created_time).split()[0],
                                'bank_code': each_student_refund_object.bank_code,
                                'bank_name': each_student_refund_object.bank_name,
                                'bank_account_code': each_student_refund_object.bank_account_code,
                                'amount': each_student_refund_object.refund_amount,
                                'txn_fee': each_student_refund_object.txn_fee,
                            }
                        )
                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
    else:
        # 傳輸有問題
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = '不好意思，系統好像出了點問題，請您告訴我們一聲並且稍後再試試看> <'
        response['data'] = None

    return JsonResponse(response)
