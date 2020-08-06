from django.shortcuts import render

# Create your views here.
def lessons_main_page(request):
    title = '開課! Quikok - 課程主頁'
    main_subjucts_list = ['國文','英文','數學']
    #if request.method == 'POST':
    #    subjects = request.POST.get('subjects')
    #    print(subjects)

    if 'subjects' in request.POST:
        if request.POST['subjects'] is not '':
            
            print(request.POST['platform'])



    return render(request, 'lesson/lessons_main_page.html', locals())