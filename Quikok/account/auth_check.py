from django.contrib.auth.models import Permission, User, Group
from account.models import student_profile, teacher_profile, user_token
from chatroom.models import chatroom_info_Mr_Q2user
import re
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
        # value = (前端給的url格式, 有權限的 auth_group_id)
        self.url_category_rules = {
            '老師會員中心': ('^/account/info/teacher.', 1,3),
            '課程管理' : ('^/account/lesson.', 1,3),
            '課程上架': ('^/lesson/ready/add.', 1,3), 
            '課程編輯': ('^/lesson/ready/edit/.', 1,3),
            '課程預覽' : ('^/lesson/main/preview/.', 1,3),
            #'上課live_house' : ('', 'member_only'), # 還沒做到
            #'聊天室主頁' : ('', 'member_only'), # 還沒做到
            '學生會員中心' : ('^/account/info/student.', 1,4),
            #'學生帳務中心' : ('', 4),
            #'學習歷程': ('', 4),
            #'方案購買': ('', 4),
            #'課程預約': ('', 4),
            # 以下為公開頁面
            '首頁' : ('/home', 'public'),
            '課程搜尋頁' : ('^/lesson/search[?]q=.', 'public'),
            '課程資訊頁' : ('^/lesson/main/view/.', 'public'),
            '註冊新老師' : ('/account/register/teacher.', 'public'),
            '註冊新學生' : ('^/account/register/student.', 'public'),
        }
    # 一次一個url檢查權限
    def find_which_page(self,url):
        self.auth_bag = {}
        for key, value in self.url_category_rules.items():
            if len(re.findall(value[0], url)) > 0:
                self.autj_bag[key] = value
        print(self.auth_bag)
        #if len(self.auth_bag) < 1:

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
            response['errMsg'] = 'Query Data Failed.'
            response['data'] = None
        return(response)
    def check_user_type(self, userID):

        if len(teacher_profile.objects.filter(auth_id=userID))> 0:
            return('teacher')
        elif len(student_profile.objects.filter(auth_id=userID)) > 0:
            return('student')
        else:
            pass
    def check_user_token(self, userID, token):
        user_token = user_token.objects.filter(authID_object=userID)
        #token_in_db = user.token
        #logout_date = user.logout_time
        #logout_only_date = logout_date.split(' ')[0] # 0是日期, 1是小時
        #logout_datetime_type = datetime.strptime(logout_only_date,"%Y-%m-%d")
        #time_has_passed = logout_datetime_type - time 
    def get_user_group_and_permisstion_group(self,userID):
        a_user = User.objects.get(userID)
        
        for group_num in a_user.groups.all():
            self.user_auth_group.append(group_num.id) # 該使用者的auth_group
        
    def create_url_rules(self):
        # 目前有的各個網站的結構以及權限分類
        pass
    #def check_url_belong_to_which_category(self, url):
    #    for url_category_name, url_pattern_and_auth_type in self.url_category_rules.items()
    #    pass
    #def write_into_db(self):
        #from .models import auth_check
        #for url_category_name, url_pattern_and_auth_type in self.url_category_rules.items():
            #auth_check.objects.update_or_create(
                #category_name = url_category_name, 
                #defaults = {'url_pattern' : url_pattern_and_auth_type[0],
                #            'url_auth_type' : url_pattern_and_auth_type[1]
                #                            },)

        #for category in self.url_category_rules.keys():
            
#re.findall('^/account/info/teacherS+','/account/info/teacherS+')
    # 先拿 url 找 url的type
       # 用正則來處理前端給的url
       # 處理出來只有前面沒有後面
       # 再用處理出來的 url去db找 type
    # 如果 url_type == public:
        #直接 success有權限
    # else
    #   用 auth_id來看他有沒有資格看