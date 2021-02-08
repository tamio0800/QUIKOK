from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
import numpy as np
# 這裡抓資料庫的資訊
from analytics.models import object_accessed_info
from datetime import datetime, timedelta, date as date_function


def quikok_dashboard(request):
    '''
    這個函式用來顯示用戶活動情形
    '''

    def get_date_range_to_today(start_date_as_datetime_format):
        today = datetime.now()
        _temp_date_range = list()

        day_delta = 0
        while start_date_as_datetime_format + timedelta(days=day_delta) < today + timedelta(days=1):
            _temp_date_range.append(
                (start_date_as_datetime_format + timedelta(days=day_delta)).strftime("%Y.%m.%d")
                )
            day_delta += 1
        return _temp_date_range
        

    # 先叫出拜訪資訊如下： <QuerySet [('127.0.0.1', datetime.datetime(2021, 2, 5, 20, 32, 4, 563362)), (), ().....]>
    daily_visits = \
        np.array(object_accessed_info.objects.values_list('timestamp', 'ip_address')).T
    # 接著清理一下，一個ip每天只能出現一次
    the_oldest_date = min(daily_visits[0])
    day_range = get_date_range_to_today(start_date_as_datetime_format = the_oldest_date)
    daily_visits[0] = [_.strftime("%Y.%m.%d") for _ in daily_visits[0]]
    # 將所有的 datetime format turn into date format
    unique_ip_daily_visits = dict()  # 用來存放資料

    for each_day in day_range:
        # 將每一日的 unique 拜訪數量記錄下來
        unique_ip_daily_visits[each_day] = \
            len(set(daily_visits[1][daily_visits[0] == each_day]))

    print(f"unique_ip_daily_visits  {unique_ip_daily_visits}")
    unique_visits_y = json.dumps([int(_) for _ in unique_ip_daily_visits.values()])
    unique_visits_x = json.dumps(day_range)

    data = {
        'unique_visits_y': unique_visits_y,
        'unique_visits_x': unique_visits_x
    }
    print(f"data {data}")
    return render(request, 'analytics/activities_dashboard.html', context=data)


