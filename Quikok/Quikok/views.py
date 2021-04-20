from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import os
import logging
from django.conf import settings

logging.basicConfig(level=logging.NOTSET) #DEBUG

@require_http_methods(['GET'])
def get_banner_bar(request):
    response = {}
    data = []
    try:
        img_path = os.path.join(settings.BASE_DIR, 'website_assets/homepage')
        # 之後再看這個路徑該怎麼修比較好
        for i, desktop_img in enumerate(os.listdir(os.path.join(img_path, 'desktop'))):
            data.append(
                {
                    'type': 'pc',
                    'sort': str(i),
                    'img_url': f'/static/homepage/desktop/{desktop_img}',
                }
            )
        for i, mobile_img in enumerate(os.listdir(os.path.join(img_path, 'mobile'))):
            data.append(
                {
                    'type': 'mobile',
                    'sort': str(i),
                    'img_url': '/static/homepage/mobile/' + mobile_img,
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
        logging.debug('Catch an exception. Quikok/views get_banner_bar', exc_info=True)
    return JsonResponse(response)
