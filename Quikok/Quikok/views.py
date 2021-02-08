from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import os

@require_http_methods(['GET'])
def get_banner_bar(request):
    response = {}
    data = []
    try:
        img_path = 'user_upload/website_assets/homepage'
        # 之後再看這個路徑該怎麼修比較好
        for i, desktop_img in enumerate(os.listdir(os.path.join(img_path, 'desktop'))):
            data.append(
                {
                    'type': 'pc',
                    'sort': str(i),
                    'img_url': '/' + img_path + '/desktop/' + desktop_img,
                }
            )
        for i, mobile_img in enumerate(os.listdir(os.path.join(img_path, 'mobile'))):
            data.append(
                {
                    'type': 'mobile',
                    'sort': str(i),
                    'img_url': '/' + img_path + '/mobile/' + mobile_img,
                }
            )
        response['status'] = 'success'
        response['errCode'] = None
        response['errMsg'] = None
        response['data'] = data
    except Exception as e:
        response['status'] = 'failed'
        response['errCode'] = '0'
        response['errMsg'] = 'Unknown Path.'
        response['data'] = None
        print(e)
    return JsonResponse(response)
