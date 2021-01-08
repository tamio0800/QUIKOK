from django.shortcuts import render
from account_finance.models import student_purchase_record
from account_finance.email_sending import email_manager
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
        #if False not in [student_authID, teacher_authID,\
        #                lesson_id, lesson_set, price,q_discount_amount]:

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
                    print(purchase_date)
                    print(payment_deadline)

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
                    'errCode': 1,
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


def confirm_lesson_order_payment_page(request):
    all_unconfirm_users = student_purchase_record.objects.filter(payment_status='unpaid')
    return render(request, 'confirm_order_payment.html',
    {'all_unconfirm_users':all_unconfirm_users})


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




