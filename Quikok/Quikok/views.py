from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import os

# Create your views here.
def homepage(request):
    title = '開課! Quikok'
    return render(request, 'homepage.html', locals())

def base_layout(request):
    return render(request, 'base_layout.html')

def test_page(request):
    return render(request, 'test.html')

def homepage_api_recommendList(request):
    if request.method == 'POST':
        qty = request.POST.get('qty', False)
        data = list()
        if qty:
            assert int(qty)
            for _ in range(int(qty)):
                data.append(
                    {
                        'id': _,
                        'title': '馬鈴薯哥哥拉丁語' + str(_),
                        'introduction': '超棒拉丁語，聽得懂不用錢之' + str(_),
                        'img_url': 'user_upload/' + 's'+ str(_) + 'ats' + str(_) + '/snapshot.png',
                    }
                )
        return JsonResponse(data, safe=False)

def homepage_api_getBannerBar(request):
    if request.method == 'POST':
        data = list()
        img_path = 'test_folder/homepage_Banner/'
        # 之後再看這個路徑該怎麼修比較好
        for i, desktop_img in enumerate(os.listdir(os.path.join(img_path, 'desktop'))):
            data.append(
                {
                    'type': 'pc',
                    'sort': i + 1,  # 非從1開始不可嗎？
                    'img_url': img_path + '/desktop/' + desktop_img,
                }
            )
        for i, mobile_img in enumerate(os.listdir(os.path.join(img_path, 'mobile'))):
            data.append(
                {
                    'type': 'mobile',
                    'sort': i + 1,  # 非從1開始不可嗎？
                    'img_url': img_path + '/mobile/' + mobile_img,
                }
            )
        return JsonResponse(data, safe=False)
    


