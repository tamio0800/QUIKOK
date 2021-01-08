from django.shortcuts import render
from account_finance.models import student_purchase_record, student_remaining_minutes_of_each_purchased_lesson_set
from account_finance.email_sending import email_manager
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info
from django.http import JsonResponse
from chatroom.consumers import ChatConsumer
from datetime import datetime, timedelta, date as date_function
from handy_functions import check_if_all_variables_are_true


def view_email_new_order_remind(request):
    return render(request, 'send_new_order_remind.html')


def storage_order(request):
    # 訂單(方案)結帳
    response = dict()
    try:
        student_authID = request.POST.get('userID', False)
        teacher_authID = request.POST.get('teacherID', False)
        lesson_id = request.POST.get('lessonID', False)
        lesson_set = request.POST.get('sales_set', False)
        price = request.POST.get('total_amount_of_the_sales_set', False)
        q_discount_amount = request.POST.get('q_discount', False)

        teacher_queryset = teacher_profile.objects.filter(auth_id= teacher_authID)
        lesson_queryset = lesson_info.objects.filter(id = lesson_id)
        if check_if_all_variables_are_true(student_authID, teacher_authID,
                        lesson_id, lesson_set, price,q_discount_amount):
            if len(teacher_queryset) and len(lesson_queryset):
                set_queryset = lesson_sales_sets.objects.filter(lesson_id=lesson_id, sales_set=lesson_set, is_open= True)
                if len(set_queryset):
                    # 學生欲使用Q幣折抵現金
                    if q_discount_amount != '0':
                        real_price = int(price) - int(q_discount_amount)
                        # 更新學生Q幣預扣餘額
                        student_obj = student_profile.objects.get(auth_id=student_authID)
                        # 如果原本就還有預扣額度尚未更新,不能覆蓋,要加上去
                        if student_obj.withholding_balance != 0:
                            student_obj.withholding_balance = \
                            student_obj.withholding_balance + int(q_discount_amount)
                        else:
                            student_obj.withholding_balance = int(q_discount_amount)
                        student_obj.save()
                    else:
                        real_price = int(price)

                    set_obj = set_queryset.first()
                    teacher_obj = teacher_queryset.first()
                    lesson_obj = lesson_queryset.first()
                    purchase_date = date_function.today()
                    payment_deadline = purchase_date+timedelta(days=6)

                    # 建立訂單
                    new_record = student_purchase_record.objects.create(
                        student_auth_id= student_authID,
                        teacher_auth_id= teacher_authID,
                        teacher_nickname= teacher_obj.nickname,
                        purchase_date = date_function.today(),
                        payment_deadline = date_function.today()+timedelta(days=6),
                        lesson_id = lesson_id,
                        lesson_name = lesson_obj.lesson_title,
                        lesson_set_id = set_obj.id,
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
                    email_notification = email_manager()
                    email_notification.system_email_new_order_and_payment_remind(**notification)

                    response = {'status':'success',
                    'errCode': None,
                    'errMsg': None,
                    'data': new_record.id}
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

#回傳訂單紀錄
def student_order_history(request):
    try:
        student_authID = request.POST.get('userID', False)
        token = request.POST.get('token', False)
        user_type = request.POST.get('type', False)
        if check_if_all_variables_are_true(student_authID, token, user_type):
            data = []
            for record in student_purchase_record.objects.filter(student_auth_id=student_authID):
                set_name = lesson_sales_sets.objects.filter(id=record.lesson_set_id).first()
                #if set_name.sales_set == 'trial':
                #    record_set_name = '試教'
                #elif set_name.sales_set == 'no_discount':
                #    record_set_name = '單堂'
                #else:
                #    lesson_time = set_name.sales_set.split[0]
                #    lesson_discount = set_name.sales_set.split[1]
                #    if '0' in lesson_discount: # 70 折-> 7折
                #        lesson_discount = set_discount.strip('0')
                #    record_set_name = f'{lesson_time}小時{lesson_discount}折'
                
                remain_info = student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(student_auth_id=student_authID,student_purchase_record_ID=record.id)
                # 假設我買了200小時的課 已經上完100小時
                # 並且預約了60小時, 老師還在確認中.
                # api31的剩餘可預約 = 40, 剩餘未進行 = 100 
                # 此時db (student_remaining_minutes_of_each_purchased_lesson_set)裡的
                # available_remaining_minutes = 40
                # withholding_minutes = 60

                record_history = {
                '狀態':record.payment_status,
                '日期':record.purchase_date,
                '老師ID':record.teacher_auth_id,
                '老師暱稱': record.teacher_nickname,
                '課程名稱': record.lesson_name,
                'lessonID': record.lesson_id,
                #record.lesson_set_id,
                '購買方案': set_name, 
                '金額':record.purchased_with_money,
                '剩餘可預約時間（分鐘）': 'remain_info.available_remaining_minutes',
                '剩餘未進行時間（分鐘）':'',
                '付款末五碼': record.part_of_bank_account_code} # 後五碼

                data.append(record_history)
                data = {
                    '匯款資訊':{
                        '銀行代碼': '088',
                        '銀行名稱': '國泰世華銀行',
                        '銀行分行': '板橋分行',
                        '銀行帳號':'012345-411153',
                        '銀行戶名': '豆沙科技股份有限公司'}

                    }


            
            response = {'status':'success',
                        'errCode': None,
                        'errMsg': None,
                        'data': ''}
        else:
            response = {'status':'failed',
            'errCode': 0,
            'errMsg': '系統沒有收到資料，請重新整理，如狀況持續可連絡客服',
            'data': None}

    except Exception as e:
        print(f'storage_order Exception {e}')
        response = {'status':'failed',
        'errCode': 3,
        'errMsg': '資料庫有問題，請稍後再試',
        'data': None}
    return JsonResponse(response)

#def confirm_lesson_order_payment_page(request):
#    all_unconfirm_users = student_purchase_record.objects.filter(payment_status='unpaid')
#    return render(request, 'confirm_order_payment.html',
#    {'all_unconfirm_users':all_unconfirm_users})


