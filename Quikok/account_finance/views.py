from django.shortcuts import render
from account_finance.models import student_purchase_record
from account.models import teacher_profile
from lesson.models import lesson_info, lesson_sales_sets, lesson_booking_info
from django.http import JsonResponse

def storage_order(request):
    response = dict()
    try:
        student_authID = request.POST.get('userID', False)
        teacher_authID = request.POST.get('teacher_id', False)
        lesson_id = request.POST.get('lesson_id', False)
        lesson_set = request.POST.get('lesson_set', False)
        price = request.POST.get('total_amount_of_the_lesson_set', False)
        
        teacher_queryset = teacher_profile.objects.filter(auth_id= teacher_authID)
        lesson_queryset = lesson_info.objects.filter(id = lesson_id)
        if False not in [student_authID, teacher_authID,\
                        lesson_id, lesson_set, price]:
            if len(teacher_queryset) and len(lesson_queryset) > 0:
                set_queryset = lesson_sales_sets.objects.filter(Q(lesson_id=lesson_id)&Q(sales_set=lesson_set))
                if len(set_queryset)>0:
                    set_obj = set_queryset.first()
                    teacher_obj = teacher_queryset.first()
                    lesson_obj = lesson_queryset.first()
                    new_record = student_purchase_record.objects.create(
                        student_auth_id= student_authID,
                        teacher_auth_id= teacher_authID,
                        teacher_nickname= teacher_obj.nickname,
                        lesson_id = lesson_id,
                        lesson_name = lesson_obj.lesson_title,
                        lesson_set_id = set_obj.id)
                    new_record.save()

                    response = {'status':'success',
                    'errCode': None,
                    'errMsg': None,
                    'data': None}
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
            print(e)
            response = {'status':'failed',
            'errCode': 2,
            'errMsg': '資料庫有問題,請稍後再試,如狀況持續可連絡客服',
            'data': None}
        return JsonResponse(response)

    
    except Exception as e:
        print(e)
        response = {'status':'failed',
        'errCode': 2,
        'errMsg': '資料庫有問題,請稍後再試,如狀況持續可連絡客服',
        'data': None}
        return JsonResponse(response)