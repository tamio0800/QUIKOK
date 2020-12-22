from django.shortcuts import render
from account_finance.models import student_purchase_record
from account.models import teacher_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info

def storage_order(request):
    response = dict()
    try:
        student_authID = request.POST.get('userID', False)
        teacher_authID = request.POST.get('teacher_id', False)
        lesson_id = request.POST.get('lesson_id', False)
        lesson_set = request.POST.get('lesson_set', False)
        price = request.POST.get('total_amount_of_the_lesson_set', False)
        
        teacher_obj = teacher_profile.objects.filter(auth_id= teacher_authID).first()
        lesson_obj = lesson_info.objects.filter(id = lesson_id).first()
        if len(teacher_obj) and len(lesson_obj) > 0:
            new_record = student_purchase_record.objects.create(
                student_auth_id= student_authID,
                teacher_auth_id= teacher_authID,
                teacher_nickname= teacher_obj.nickname,
                lesson_id = lesson_id,
                lesson_name = lesson_obj.lesson_title,
                lesson_set_id = '',
                part_of_bank_account_code = '',
                payment_status='unpaid')

            response = {'status':'success',
            'errCode': None,
            'errMsg': None,
            'data': None}
            return JsonResponse(response)
        else:
            response = {'status':'failed',
            'errCode': 1,
            'errMsg': '系統找不到老師或該門課程，請稍後再試，如狀況持續可連絡客服',
            'data': None}

    
    except Exception as e:
        print(e)
        response = {'status':'failed',
        'errCode': 2,
        'errMsg': '資料庫有問題,請稍後再試,如狀況持續可連絡客服',
        'data': None}
        
        return JsonResponse(response)