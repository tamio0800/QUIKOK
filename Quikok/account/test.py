from django.contrib.auth.models import Permission, User, Group
from account.models import student_profile, teacher_profile, user_token
from chatroom.models import chatroom_info_Mr_Q2user
import re
from datetime import datetime, timedelta
from .views import auth_check

class test_auth_check:
    def check_user_token(self, userID, token):
        token_obj = user_token.objects.filter(authID_object=userID).first()
        #token_in_db = token_obj.token
        time = datetime.now()
        logout_date = token_obj.logout_time
        logout_datetime_type = datetime.strptime(logout_date.split('.')[0],"%Y-%m-%d %H:%M:%S")
        time_result = logout_datetime_type - time
        # 登出實現-現在時間<0 則超過時效
        if time_result.days < 0:
            print(time_result)