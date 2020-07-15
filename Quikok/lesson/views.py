from django.shortcuts import render

# Create your views here.
def lessons_main_page(request):
    #title = '開課! Quikok - 課程主頁'
    return render(request, 'lesson/lessons_main_page.html')