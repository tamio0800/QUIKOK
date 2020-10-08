from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import os
from django.contrib.auth.models import User
from account.models import student_profile, teacher_profile, specific_available_time, general_available_time
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
from account.models import teacher_profile
from lesson.models import lesson_info, lesson_reviews
from lesson.lesson_tools import lesson_manager
from django.contrib.auth.decorators import login_required

@login_required
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
    qty = request.GET.get('qty', False) # 暫定六堂課
    #ordered_by = request.GET.get('ordered_by', False)
    #filtered_by = request.GET.get('filtered_by', False)
    response = {}
    print(qty)
    #print(ordered_by)
    #print(filtered_by)
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
                    big_title = df_lesson['big_title'][each_row_num],
                    little_title = df_lesson['little_title'][each_row_num],
                    teacher = teacher_id,
                    lesson_title = df_lesson['lesson_title'][each_row_num],
                    price_per_hour = df_lesson['price_per_hour'][each_row_num],
                    highlight_1 = df_lesson['highlight_1'][each_row_num],
                    highlight_2 = df_lesson['highlight_2'][each_row_num],
                    highlight_3 = df_lesson['highlight_3'][each_row_num],
                    lesson_intro = df_lesson['lesson_intro'][each_row_num],
                    how_does_lesson_go = df_lesson['how_does_lesson_go'][each_row_num],
                    target_students = df_lesson['target_students'][each_row_num],
                    lesson_remarks = df_lesson['lesson_remarks'][each_row_num],
                    lesson_background_folder = df_lesson['lesson_background_folder'][each_row_num],
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


def lesson_manage(request):
    # 新增課程
    response = {}
    # 當學生瀏覽課程、老師預覽/修改上架內容
    # 這段功能還沒寫
    if request.method == 'GET':
        
        lesson_id = request.POST.get('lesson_id', False)
        show_lesson = lesson_info.objects.get(id = lesson_id)
        big_title = show_lesson.big_title
        little_title = show_lesson.little_title
        title_color = show_lesson.title_color
        default_background_picture = show_lesson.default_background_picture
        background_picture = show_lesson.background_picture
        lesson_title = show_lesson.lesson_title
        price_per_hour= show_lesson.price_per_hour
        trial_class_price = show_lesson.trial_class_price
        discount_price = show_lesson.discount_price
        highlight_1 = show_lesson.highlight_1
        highlight_2 = show_lesson.highlight_2
        highlight_3 = show_lesson.highlight_3
        lesson_intro = show_lesson.lesson_intro 
        how_does_lesson_go = show_lesson.how_does_lesson_go
        target_students = show_lesson.target_students
        syllabus = show_lesson.syllabus
        lesson_remarks = show_lesson.lesson_remarks
        lesson_attributes = show_lesson.lesson_attributes
        selling_status = show_lesson.selling_status
        #return render(request, 'lesson/create_lesson.html')



        return render(request, 'lesson/create_lesson.html')

    if request.method == 'POST':
        action = request.POST.get('action', False) # 新增或修改課程
        lesson_id = request.POST.get('lessonID', False)
        # 修改應該只比新增多 "課程id" 這個資訊要拿
        auth_id = request.POST.get('userID', False)
        #auth_id = 2 # 測試用
        teacher_username = User.objects.get(id = auth_id).username
        # 用老師username當key從auth找profile
        teacher = teacher_profile.objects.get(username = teacher_username)
        
        big_title = request.POST.get('big_title', False)
        little_title= request.POST.get('little_title', False)
        title_color= request.POST.get('title_color', False)
        default_background_picture= request.POST.get('default_background_picture', False)
        background_picture= request.POST.get('background_picture', False)
        lesson_title = request.POST.get('lesson_title', False)
        
        price_per_hour= request.POST.get('price_per_hour', False)
        #price_per_hour = 300
        unit_class_price = request.POST.get('unitClassPrice', 0)
        #unit_class_price = 300
        #單節費用 有勾選前端回傳鐘點費金額 無勾選前端回傳null
        trial_class_price = request.POST.get('trialClassPrice', 0)
        discount_price = request.POST.get('discountPrice', 0)
        highlight_1 = request.POST.get('highlight_1', False) 
        highlight_2 = request.POST.get('highlight_2', False)
        highlight_3 = request.POST.get('highlight_3', False)
        lesson_intro = request.POST.get('lesson_intro', False)
        how_does_lesson_go = request.POST.get('how_does_lesson_go', False)
        target_students = request.POST.get('target_students', False)
        syllabus = request.POST.get('syllabus', False)
        lesson_remarks = request.POST.get('lesson_remarks', False)
        lesson_attributes = request.POST.get('lesson_attributes', False)
        selling_status = request.POST.get('sellStatus', False)


        
        if action == 'editLesson': 
            # 如果 lesson_id 有值表示是要修改欄位,多加一個action條件防意外
            if  [lesson_id,teacher, lesson_title, price_per_hour, lesson_intro]:
                lesson_obj = lesson_info.objects.filter(id = lesson_id)
                if lesson_obj:
                    lesson_obj.update(
                        big_title = big_title,
                        little_title= little_title,
                        title_color = title_color,
                        default_background_picture= default_background_picture,
                        background_picture = background_picture,
                        lesson_title = lesson_title,
                        price_per_hour= price_per_hour,
                        unit_class_price = unit_pclass_price,
                        trial_class_price = trial_class_price,
                        discount_price = discount_price,
                        highlight_1 = highlight_1,
                        highlight_2 = highlight_2,
                        highlight_3 = highlight_3,
                        lesson_intro = lesson_intro,
                        how_does_lesson_go = how_does_lesson_go,
                        target_students = target_students,
                        syllabus = syllabus,
                        lesson_remarks = lesson_remarks,
                        lesson_attributes=  lesson_attributes,
                        selling_status = selling_status
                    )
                    response['status'] = 'success'
                    response['errCode'] = None
                    response['errMsg'] = None
                else:
                    response['status'] = 'failed'
                    response['errCode'] = 0
                    response['errMsg'] = 'update failed:cannot find this lesson'
            
            else:            # 資料傳輸有問題
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = 'wrong data: false in required field'        


        # 新增lesson 時的必填欄位, 不得為 False, 雖然前端有做處理但這邊再防傳輸問題
        elif  action == 'createLesson':
            if [selling_status, teacher, lesson_title, price_per_hour, lesson_intro]:
                lesson_info.objects.create(
                    #lesson_id = lesson_id, 
                    #teacher =teacher 
                    teacher = teacher, #測試
                    big_title = big_title,
                    little_title= little_title,
                    title_color = title_color,
                    default_background_picture= default_background_picture,
                    background_picture = background_picture,
                    lesson_title = lesson_title,
                    price_per_hour= price_per_hour,
                    unit_class_price = unit_class_price,
                    trial_class_price = trial_class_price,
                    discount_price = discount_price,
                    highlight_1 = highlight_1,
                    highlight_2 = highlight_2,
                    highlight_3 = highlight_3,
                    lesson_intro = lesson_intro,
                    how_does_lesson_go = how_does_lesson_go,
                    target_students = target_students,
                    syllabus = syllabus,
                    lesson_remarks = lesson_remarks,
                    lesson_attributes=  lesson_attributes,
                    selling_status = selling_status
                    ).save()
                response['status'] = 'success'
                response['errCode'] = None
                response['errMsg'] = None
            else:
                response['status'] = 'failed'
                response['errCode'] = '1'
                response['errMsg'] = 'wrong data: false in required field'
        else:
            # action不等於任何值
            response['status'] = 'failed'
            response['errCode'] = '2'
            response['errMsg'] = 'what is action?'
    print(response)
    #return JsonResponse(response)    
    return render(request, 'lesson/create_lesson.html')#後端測試用


    #lesson_info.objects.create(
    #lesson_id = lesson_id, 
    #teacher = teacher_id,
    #big_title = big_title,
    #little_title= little_title,
    #default_background_picture= default_background_picture,
    #background_picture = background_picture,
    #lesson_title = lesson_title,
    #price_per_hour= price_per_hour,
    #highlight_1 = highlight_1,
    #highlight_2 = highlight_2,
    #highlight_3 = highlight_3,
    #lesson_intro = lesson_intro,
    #how_does_lesson_go = how_does_lesson_go,
    #target_students = target_students,
    #syllabus = syllabus,
    #lesson_remarks = lesson_remarks,
    #lesson_attributes=  lesson_attributes,
    #).save()

# 用 lesson_tools create 課程的方式
            #lesson_create = lesson_manager()
            #lesson_create.create_lesson(
            #teacher_id = teacher_id,
            #big_title = big_title,
            #little_title= little_title,
            #default_background_picture= request.POST.get('default_background_picture', False),
            #background_picture= request.POST.get('background_picture', False),
            #lesson_title = request.POST.get('lesson_title', False),
            #discount_price= request.POST.get('discountPrice', False),
            #price_per_hour= request.POST.get('price_per_hour', False),
            #trial_class_price = request.POST.get('trialClassPrice', False),
            #highlight_1 = request.POST.get('highlight_1', False) ,
            #highlight_2 = request.POST.get('highlight_2', False),
            #highlight_3 = request.POST.get('highlight_3', False),
            #lesson_intro = request.POST.get('lesson_intro', False),
            #how_does_lesson_go = request.POST.get('how_does_lesson_go', False),
            #target_students = request.POST.get('target_students', False),
            #syllabus = request.POST.get('syllabus', False),
            #lesson_remarks = request.POST.get('lesson_remarks', False),
            #lesson_attributes = request.POST.get('lesson_attributes', False)

            #)