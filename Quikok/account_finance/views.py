from django.shortcuts import render
from account_finance.models import student_purchase_record
from account_finance.email_sending import email_manager
from account.models import teacher_profile
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

        if q_discount_amount != '0':
            real_price = int(price) - int(q_discount_amount)
        else:
            real_price = int(price)
        teacher_queryset = teacher_profile.objects.filter(auth_id= teacher_authID)
        lesson_queryset = lesson_info.objects.filter(id = lesson_id)
        if check_if_all_variables_are_true(student_authID, teacher_authID,
                        lesson_id, lesson_set, price,q_discount_amount):
        #if False not in [student_authID, teacher_authID,\
        #                lesson_id, lesson_set, price,q_discount_amount]:

            if len(teacher_queryset) and len(lesson_queryset):
                set_queryset = lesson_sales_sets.objects.filter(lesson_id=lesson_id, sales_set=lesson_set, is_open= True)
                
                if len(set_queryset):

                    set_obj = set_queryset.first()
                    teacher_obj = teacher_queryset.first()
                    lesson_obj = lesson_queryset.first()
                    purchase_date = date_function.today()
                    payment_deadline = purchase_date+timedelta(days=6)

                    new_record = student_purchase_record.objects.create(
                        student_auth_id= student_authID,
                        teacher_auth_id= teacher_authID,
                        teacher_nickname= teacher_obj.nickname,
                        purchase_date = purchase_date,
                        payment_deadline = payment_deadline,
                        lesson_id = lesson_id,
                        lesson_name = lesson_obj.lesson_title,
                        lesson_set_id = set_obj.id,
                        price = price,
                        purchased_with_q_points = q_discount_amount,
                        purchased_with_money=real_price
                        )
                    new_record.save()

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
                    email_notification.system_email_new_order_payment_remind(**notification)

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


