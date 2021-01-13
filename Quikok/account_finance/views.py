from django.shortcuts import render
from account_finance.models import student_purchase_record, student_remaining_minutes_of_each_purchased_lesson_set
from account_finance.email_sending import email_manager, email_for_edony
from account.models import teacher_profile, student_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info
from django.http import JsonResponse
from chatroom.consumers import ChatConsumer
from datetime import datetime, timedelta, date as date_function
from handy_functions import check_if_all_variables_are_true
from django.views.decorators.http import require_http_methods


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
                            # tata:
                            #   這個可以寫成 >>
                            #   student_obj.withholding_balance += int(q_discount_amount)
                        else:
                            student_obj.withholding_balance = int(q_discount_amount)
                        student_obj.save()
                    else:
                        real_price = int(price)

                    set_obj = set_queryset.first()
                    teacher_obj = teacher_queryset.first()
                    lesson_obj = lesson_queryset.first()
                    purchase_date = date_function.today()
                    payment_deadline = purchase_date + timedelta(days=6)

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

#回傳訂單紀錄api, 我的存摺頁
def student_order_history(request):
    try:
        student_authID = request.POST.get('userID', False)
        token = request.POST.get('token', False)
        user_type = request.POST.get('type', False)
        if check_if_all_variables_are_true(student_authID, token, user_type):
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
                    lesson_time = set_name.sales_set.split[0]
                    total_time = int(lesson_time)*60 # 小時轉成分鐘
                #    lesson_discount = set_name.sales_set.split[1]
                #    if '0' in lesson_discount: # 70 折-> 7折
                #        lesson_discount = set_discount.strip('0')
                #    record_set_name = f'{lesson_time}小時{lesson_discount}折'
                
                # 如果這筆訂單還沒從unpaid改成paid, 剩餘時數的table也就還沒長出來
                # 所以必須把分付款狀態來處理
                if record.payment_status in ['paid','refunding','refunded', 'cancel_after_paid']:
                    remain_time_info = student_remaining_minutes_of_each_purchased_lesson_set.objects.get(student_purchase_record_id=record.id)
                    total_unconfirmed_time = total_time - remain_time_info.confirmed_consumed_minutes
                    available_remaining_minutes = remain_time_info.available_remaining_minutes
                else:
                    available_remaining_minutes = ''
                    total_unconfirmed_time = ''

                
                record_history = {
                'purchase_recordID':record.id,
                'payment_status':record.payment_status,
                'purchase_date':record.purchase_date,
                'teacher_authID':record.teacher_auth_id,
                'teacher_nickname': record.teacher_nickname,
                'lesson_title': record.lesson_title,
                'lessonID': record.lesson_id,
                'lesson_sale_set': set_name.sales_set, 
                'purchased_with_money':record.purchased_with_money,
                'available_remaining_minutes': available_remaining_minutes,
                'total_unconfirmed_time': total_unconfirmed_time} #全部時數減掉已confirm完課的時數,主要是給老師看的
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
            'data': None}

    except Exception as e:
        print(f'storage_order Exception {e}')
        response = {'status':'failed',
        'errCode': 1,
        'errMsg': '資料庫有問題，請稍後再試',
        'data': None}
    return JsonResponse(response)


# 編輯訂單狀態api, 包含取消訂單
def student_edit_order(request):
    try:
        student_authID = request.POST.get('userID', False)
        token = request.POST.get('token', False)
        user_type = request.POST.get('type', False)
        purchase_recordID = request.POST.get('purchase_recordID', False)
        status_update = request.POST.get('status_update', False)
        # 0-付款完成/1-申請退款/2-申請取消
        user5_bank_code = request.POST.get('part_of_bank_account_code', False)

        if check_if_all_variables_are_true(student_authID, token, user_type,
                            purchase_recordID, status_update, user5_bank_code):
            # 首先查詢訂單狀態
            record = student_purchase_record.objects.filter(id = purchase_recordID).first()
            # 訂單已付款
            if record.payment_status in ['paid','refunding','refunded', 'cancel_after_paid']:
                pass
            # 訂單尚未付款
            elif record.payment_status == 'unpaid':
                if status_update == '0': # 學生已付款,接著我們要對帳
                    
                    record.payment_status = 'refunding'
                    record.part_of_bank_account_code = user5_bank_code
                    record.save()
                    email_to_edony = email_for_edony()
                    email_to_edony.send_email(student_authID=student_authID,
                      user5_bank_code =user5_bank_code, total_price = record.purchased_with_money  )

            else:
                pass
                    
            response = {'status':'success',
                        'errCode': None,
                        'errMsg': None,
                        'data': None}
        else:
            response = {'status':'failed',
            'errCode': 2,
            'errMsg': '資料庫有問題，請稍後再試',
            'data': None}

        
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
                        unconsumed_minutes = \
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
                                'unconsumed_minutes': unconsumed_minutes,
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
                response['data'] = None

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




