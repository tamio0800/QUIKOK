from django.contrib.auth.models import Permission, User, Group
from account.models import student_profile, teacher_profile, user_token
from chatroom.models import chatroom_info_Mr_Q2user
import re
from datetime import datetime, timedelta
# 跟權限確認有關係的功能
# 像一道道閘門一樣每個網頁去確認權限
# 有過/沒過, 回傳 1,0, 並藉此控制回傳給前端的responce
# 只要有一個沒過就會回傳0,並不再繼續檢查
# 這是因為現在做測試版本每個user都會至少有兩個群組,例如:pilot_test, student
# 由於測試群組不能看到未開放的頁面,因此會優先檢查
# 群組權限如果都過最後檢查個人權限,只有個人可以看到的頁面
class auth_check_manager:
    def __init__(self):
        self.user_auth_group = list()
        self.auth_page = {}
        # value = (前端給的url格式, 有權限的 auth_group_id)
        self.url_category_rules = {
            '老師會員中心': ('^/account/info/teacher.', 1,3,5),
            '課程管理' : ('^/account/lesson.', 1,3,5),
            '課程上架': ('^/lesson/ready/add.', 1,3,5), 
            '課程編輯': ('^/lesson/ready/edit/.', 1,3,5),
            '課程預覽' : ('^/lesson/main/preview/.', 1,3,5),
            #'上課live_house' : ('', 'member_only'), # 還沒做到
            #'聊天室主頁' : ('', 'member_only'), # 還沒做到
            '學生會員中心' : ('^/account/info/student.', 3,4,5),
            #'學生帳務中心' : ('', 4),
            #'學習歷程': ('', 4),
            #'方案購買': ('', 4),
            #'課程預約': ('', 4),
            # 以下為公開頁面
            '首頁' : ('/home', 'public'),
            '課程搜尋頁' : ('^/lesson/search[?]q=.', 'public'),
            '課程資訊頁' : ('^/lesson/main/view/.', 'public'),
            '註冊新老師' : ('/account/register/teacher.', 'public'),
            '註冊新學生' : ('^/account/register/student.', 3,4,5),
        }
    # 確認前端這次傳來的url屬於哪個權限範圍(一次一個url檢查權限,bag裡只應該有一筆資料)
    def find_auth_page(self,url):
        for key, value in self.url_category_rules.items():
            if len(re.findall(value[0], url)) > 0:
                self.auth_page[key] = value
        print(self.auth_page)

    # 管理給前端的回應
    def response_to_frontend(self,num):
        response = dict()
        if num == 0:
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = {'authority' : True }
            
        elif num == 1:
            response['status'] = 'failed'
            response['errCode'] = '0'
            response['errMsg'] = 'Received Arguments Failed.'
            response['data'] = None
        elif num == 2:
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = 'Page is not exist.'
            response['data'] = None
        elif num == 3:
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = 'Please login.'
            response['data'] = {'authority' : False }
        elif num == 4:
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = 'Query Data Failed.'
            response['data'] = None
        elif num == 5:
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = 'Permission denied.'
            response['data'] = {'authority' : False }

        return(response)
    def check_user_type(self, userID):
        if len(teacher_profile.objects.filter(auth_id=userID))> 0:
            return('teacher')
        elif len(student_profile.objects.filter(auth_id=userID)) > 0:
            return('student')
        else:
            pass
    # gate.1 url種類如果是public一律有權限
    def check_url_is_public(self):
        for info_key,auth_info in self.auth_page.items():
            for info in auth_info:
                if info == 'public': # public頁面,一律有權限
                    return(1)
                else:
                    return(0)
    # gate.2 時效與token檢查
    def check_user_token(self, userID, token):
        token_obj = user_token.objects.filter(authID_object=userID).first()
        time = datetime.now()
        logout_date = token_obj.logout_time
        logout_datetime_type = datetime.strptime(logout_date.split('.')[0],"%Y-%m-%d %H:%M:%S")
        time_result = logout_datetime_type - time
        # 登出時間-現在時間<0 則超過時效
        if time_result.days < 0:
            return(0)
        else:
            if token == token_obj.token:
                return(1)
            else:
                return(0)
    # gate.3 依權限分類劃分
    #使用者的權限分類
    def get_user_group_and_permission_group(self,userID):
        a_user = User.objects.filter(userID).first()
        for group_num in a_user.groups.all():
            self.user_auth_group.append(group_num.id) # 該使用者的auth_groupID
    # 比對授權號碼    
    def check_auth_page_and_permission(self):
        for info_key,auth_info in self.auth_page.items():
            for info in auth_info:
                if info in self.user_auth_group:
                    return(1)
                else:
                    return(0)
           
    def check_all_gate_and_responce(self,**kwargs):
        userID = kwargs['userID']
        url = kwargs['url']
        token = kwargs['token']
        self.get_user_group_and_permission_group(userID)
        # superuser:edony 擁有所有權限
        if 5 in self.user_auth_group:
            response = self.response_to_frontend(0)
            print('pass auth check')
        # 確認網址屬性
        self.find_auth_page(url)
        if len(self.auth_page)<0:
            response = self.response_to_frontend(2)
        else: #gate1
            is_public = self.check_url_is_public()
            if is_public == 1:
                response = self.response_to_frontend(0)
                print('pass auth check')
            elif is_public == 0:
                # gate2
                is_token_match = self.check_user_token(userID,token)
                if is_token_match ==0:
                    response = self.response_to_frontend(3)
                elif is_token_match ==1:
                    # gate3
                    self.get_user_group_and_permission_group(userID)
                    is_perm_match = self.check_auth_page_and_permission()
                    if is_perm_match == 0:
                        response = self.response_to_frontend(5)
                    elif is_perm_match == 1:
                        response = self.response_to_frontend(0)
                        print('pass auth check')
        print(response)
        return(response)


