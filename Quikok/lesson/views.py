from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import os
from account.models import student_profile, teacher_profile, specific_available_time, general_available_time
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage
# Create your views here.
import pandas as pd
from account.models import teacher_profile
from lesson.models import lesson_info, lesson_reviews

def lessons_main_page(request):
    title = '開課! Quikok - 課程主頁'
    main_subjucts_list = ['國文','英文','數學']
    #if request.method == 'POST':
    #    subjects = request.POST.get('subjects')
    #    print(subjects)
    #if 'subjects' in request.POST:
    #    if request.POST['subjects'] is not '':
    #        print(request.POST['platform'])
    
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
    # http://127.0.0.1:8000/api/lesson/recommend_list?qty=1&ordered_by=%22x%22&filtered_by=%22X%22
    qty = request.GET.get('qty', False)
    ordered_by = request.GET.get('ordered_by', False)
    filtered_by = request.GET.get('filtered_by', False)
    response = {}
    print(qty)
    print(ordered_by)
    print(filtered_by)
    if (not qty or not ordered_by or not filtered_by):
        # 收取的資料不正確
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'invalid query'
        response['data'] = None
        return JsonResponse(response)
    else:
        # 收取的資料正確，準備撈資料回傳
        # order_by 跟 filtered_by 暫時不寫
        qty = int(qty)
        _data = []
        lesson_objects = lesson_info.objects.filter()[:qty]
        for each_lesson_object in lesson_objects:
            lesson_attributes = {}
            lesson_attributes['teacher_thumbnail'] = os.path.join(each_lesson_object.teacher.picture_folder, 'thumbnail.png')
            lesson_attributes['teacher_nickname'] = each_lesson_object.teacher.nickname
            available_time = {}
            teacher_general_time_obj = each_lesson_object.teacher.general_time
            for each_week in teacher_general_time_obj.filter():
                available_time[each_week.week] = each_week.time
            lesson_attributes['teacher_general_availabale_time'] = available_time
            lesson_attributes['teacher_id_approved'] = each_lesson_object.teacher.id_approved
            lesson_attributes['teacher_education_approved'] = each_lesson_object.teacher.education_approved
            lesson_attributes['teacher_work_approved'] = each_lesson_object.teacher.work_approved
            lesson_attributes['teacher_other_approved'] = each_lesson_object.teacher.other_approved
            lesson_attributes['lesson_title'] = each_lesson_object.lesson_title
            lesson_attributes['highlight_1'] = each_lesson_object.highlight_1
            lesson_attributes['highlight_2'] = each_lesson_object.highlight_2
            lesson_attributes['highlight_3'] = each_lesson_object.highlight_3
            lesson_attributes['price_per_hour'] = each_lesson_object.price_per_hour
            _data.append(lesson_attributes)
        
        response['status'] = 'success'
        response['errCode'] = None
        response['errMsg'] = None
        response['data'] = _data
        return JsonResponse(response)
        


            

# 課程相關：課程名稱、課程特點1、課程特點2、課程特點3、課程時薪

    
    return render(request, 'lesson/lessons_main_page.html', locals())



def import_lesson(request):
    title = '批次匯入課程'
    folder_where_are_uploaded_files_be = 'temp' # 
    if request.method == 'POST':
        fs = FileSystemStorage(location=folder_where_are_uploaded_files_be)
        for each_file in request.FILES.getlist("files"):
            fs.save(each_file.name, each_file)
            if each_file.name.endswith(('xlsx', 'xls')):
                df_lesson = pd.read_excel(os.path.join(folder_where_are_uploaded_files_be, each_file.name))
                for each_row_num in range(df_lesson.shape[0]):
                    #print(each_row)
                    teacher_id = teacher_profile.objects.get(id = each_row_num+1) #ForeignKey
                    lesson_info.objects.create(
                    lesson_id = df_lesson['lesson_id'][each_row_num],
                    teacher = teacher_id,
                    lesson_title = df_lesson['lesson_title'][each_row_num],
                    price_per_hour = df_lesson['price_per_hour'][each_row_num],
                    highlight_1 = df_lesson['highlight_1'][each_row_num],
                    highlight_2 = df_lesson['highlight_2'][each_row_num],
                    highlight_3 = df_lesson['highlight_3'][each_row_num],
                    lesson_intro = df_lesson['lesson_intro'][each_row_num],
                    how_does_lesson_go = df_lesson['how_does_lesson_go'][each_row_num],
                    lesson_remarks = df_lesson['lesson_remarks'][each_row_num],
                    lesson_picture_folder = '',
                    syllabus = df_lesson['syllabus'][each_row_num],
                    lesson_appendix_folder ='',
                    lesson_attributes =df_lesson['lesson_attributes'][each_row_num],
                    lesson_avg_score = 0,
                    lesson_reviewed_times = 0,
                    ).save()
                    print('成功匯入課程:'+ df_lesson['lesson_title'][each_row_num])
            else:
                print('我只收xlsx,xls檔')        
        os.unlink(os.path.join(folder_where_are_uploaded_files_be, each_file.name))
    return render(request, 'lesson/import_lesson.html',locals())