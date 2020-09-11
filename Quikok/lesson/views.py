from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
# Create your views here.

from account.models import teacher_profile
from lesson.models import lesson_info, lesson_reviews


def lessons_main_page(request):
    title = '開課! Quikok - 課程主頁'
    main_subjucts_list = ['國文','英文','數學']
    #if request.method == 'POST':
    #    subjects = request.POST.get('subjects')
    #    print(subjects)

    if 'subjects' in request.POST:
        if request.POST['subjects'] is not '':
            
            print(request.POST['platform'])
    
    ## 08.26 建了許多老師假資料後回頭來串接這邊
    current_teacher = teacher_profile.objects.all()
    return render(request, 'lesson/lessons_main_page.html', locals())


@require_http_methods(['GET'])
def get_lesson_card(request):
    # 20200911 暫時不開發排序、篩選部分
    # 接收：需要多少小卡(int)、排序依據(string)、篩選依據(string)
    # 需要回傳「相同數量」的課程小卡，包含：
    # 老師相關：老師圖像、老師暱稱、老師有空的general時段、身分認證、學歷認證、經歷認證、其他認證
    # 課程相關：課程名稱、課程特點1、課程特點2、課程特點3、課程時薪
    qty = request.GET.get('qty', False)
    ordered_by = request.GET.get('order_by', False)
    filtered_by = request.GET.get('filtered_by', False)
    response = {}
    if (not qty or not ordered_by or not filtered_by):
        # 收取的資料不正確
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'invalid query'
        response['data'] = None
        return JsonResponse(response)
    else:
        qty = int(qty)
        _data = []
        lesson_objects = lesson_info.objects.filter()


    
    return render(request, 'lesson/lessons_main_page.html', locals())