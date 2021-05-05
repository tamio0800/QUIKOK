from django.contrib.auth.models import Permission, User, Group
from account.models import student_profile, teacher_profile, user_token
import re, logging
from datetime import datetime, timedelta

#測試用
# from account.auth_check import auth_check_manager
# a = auth_check_manager()
#a.check_all_gate_and_responce(userID = 9, url = '/account/info/teacher', token ='pbkdf2_sha256$216000$yMyEFKhgkT7L$hoiStkV4HVl4iXZbwg7OKzBZJ7n+82KXWGWPE3WvKb8=')

# 跟權限確認有關係的功能
# 像一道道閘門一樣每個網頁去確認權限
# 有過/沒過, 回傳 1,0, 並藉此控制回傳給前端的responce
# 只要有一個沒過就會回傳0,並不再繼續檢查
# 這是因為現在做測試版本每個user都會至少有兩個群組,例如:pilot_test, student
# 由於測試群組不能看到未開放的頁面,因此會優先檢查
# 群組權限如果都過最後檢查個人權限,只有個人可以看到的頁面


logging.basicConfig(level=logging.NOTSET) #DEBUG
logger_account = logging.getLogger('account_info')

class auth_check_manager:
    def __init__(self):
        self.user_auth_group = list()
        self.auth_page = {}
        # value = (前端給的url格式, 有權限的 auth_group的id)  auth_group為table名稱
        self.url_category_rules = {
            '老師會員中心': ('^/account/info/teacher', 2,3,5),
            '課程管理' : ('^/account/lesson', 2,3,5),
            '課程上架': ('^/lesson/ready/add', 2,3,5), 
            '課程編輯': ('^/lesson/ready/edit/.', 2,3,5),
            '課程預覽' : ('^/lesson/main/preview/.', 2,3,5),
            #'上課live_house' : ('', 'member_only'), # 還沒做到
            #'聊天室主頁' : ('', 'member_only'), # 還沒做到
            '學生會員中心' : ('^/account/info/student', 1,4,5),
            '商品結帳' :('^/store/checkout',1,2,3,4,5),
            '帳務中心' :('^/account/finance',1,2,3,4,5),
            '預約管理' :('^/account/reservation',2,3,5),
            '課程預約' :('^/lesson/appointment',1,4,5),
            '學習歷程' :('^/account/study',1,4,5),
            # 以下為公開頁面
            '首頁' : ('/home', 'public'),
            '課程搜尋頁' : ('^/lesson/search|/lesson/search[?]q=.*', 'public'),
            '課程資訊頁' : ('^/lesson/main/view/.*', 'public'),
            '註冊新老師' : ('^/account/register/teacher.*', 'public'),
            '註冊新學生' : ('^/account/register/student.*', 'public'),
            '部落格首頁':('^/blog/main', 'public'),
            '部落格文章內頁':('^/blog/post/.*', 'public'),
            '訪客上架':('^/lesson/guestready', 'public'),
            '入口頁':('^/landing', 'public'),
            '老師/學生資訊頁(公開)':('^/account/profile/\d*', 'public'),
            '題庫方案頁':('^/questionBank/program/.*', 'public')
            
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
        # 有權限
        if num == 0:
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = None
            response['data'] = {'authority' : True }
        # 沒有收到資料    
        elif num == 1:
            response['status'] = 'failed'
            response['errCode'] = '0'
            response['errMsg'] = 'not received data'
            response['data'] = None
        # 萬一有頁面不存在..前端會統一導向首頁,正常情況不會走到這步
        # 是正則表達無法判斷是哪一頁的時候防掛掉用的
        elif num == 2:
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] =  'Page is not exist.'
            response['data'] = {'authority' : False }
        elif num == 3: # token unmatch, 超過時效或沒登入的訪客進入該頁
            response['status'] = 'failed'
            response['errCode'] = None
            response['errMsg'] = 'Please login.'
            response['data'] = {'authority' : False }
        # 暫時未使用...都用num==0回傳
        elif num == 4:
            response['status'] = 'failed'
            response['errCode'] = '1'
            response['errMsg'] = 'Query Data Failed.'
            response['data'] = None
        elif num == 5: # 時效內登入中但沒有權限
            response['status'] = 'success'
            response['errCode'] = None
            response['errMsg'] = 'Permission denied.'
            response['data'] = {'authority' : False }
  
        return(response)
    # 這是個很常用到的功能, 但權限檢查用不到
    def check_user_type(self, userID):

        if userID == 1 or userID == '1':
            return('system')        
            # 目前的systemID就只有1,將來可能會有很多組
            # 但如果要新增很多組system要注意身分問題,system auth_id=1是老師, 
            # 在例如回傳系統聊天室的時候為了拿大頭照跟nickname,
            # 會去teacher_profile拿,如果將來的系統又有學生,那類似這種情況時會出錯
        else:
            if teacher_profile.objects.filter(auth_id=userID).count()>0:
                return('teacher')
            elif student_profile.objects.filter(auth_id=userID).count()>0:
                return('student')
            else:
                return(0)
    # gate.1 url種類如果是public, 如果有token還是會比對是否一致,沒token會直接放行
    def check_url_is_public(self):
        for info_key,auth_info in self.auth_page.items():
            # if any(_ == 'public' for _ in auth_info)
            if 'public' in auth_info:
                return(1)
            else:
                return(0)
    # gate.2 時效與token檢查
    def check_user_token(self, userID, token):
        if int(userID) >0:
            token_obj = user_token.objects.filter(authID_object=userID).first()
            print('token in db:')
            print(token_obj.token)
            time = datetime.now()
            logout_date = token_obj.logout_time
            logout_datetime_type = datetime.strptime(logout_date.split('.')[0],"%Y-%m-%d %H:%M:%S")
            time_result = logout_datetime_type - time
            # 登出時間-現在時間<0 則超過時效
            if time_result.days < 0:
                return(0)
            else: # 登入時間內,token unmatch也是沒有權限
                if token == token_obj.token:
                    return(1)
                else: # token unmatch
                    return(2)
        else:
            return(0)
    # gate.3 依權限分類劃分
    #使用者的權限分類
    def get_user_group_and_permission_group(self,userID):
        a_user = User.objects.filter(id = userID).first()
        for group_num in a_user.groups.all():
            self.user_auth_group.append(group_num.id) # 該使用者的auth_groupID
            print('self.user_auth_group_1')
            print(self.user_auth_group)
    # 比對授權號碼    
    def check_auth_page_and_permission(self):
        #print('self.auth_page')
        print('self.user_auth_group_2')
        print(self.user_auth_group)

        for info_key,info_value in self.auth_page.items():
            #for info in auth_info:
                if any(auth_num in self.user_auth_group for auth_num in info_value):
                    return(1) # 網頁授權的group有在user的group中
                else:
                    return(0)
           
    def check_all_gate_and_responce(self,**kwargs):
        userID = kwargs['userID']
        url = kwargs['url']
        token = kwargs['token']
        logger_account.info('啟動權限檢查')
        logger_account.info(f'接收前端資料:userID: {userID},:url: {url}, token: {token}')
        
        try:
            if int(userID) >0: # -1目前是訪客
                self.get_user_group_and_permission_group(userID)
            else:
                self.user_auth_group = list() # 訪客權限的代號

            # 5是superuser:edony 擁有所有權限
            if 5 in self.user_auth_group:
                response = self.response_to_frontend(0)
                print('pass auth check')
            else:    # 確認網址屬性
                self.find_auth_page(url)
                if len(self.auth_page)<0:
                    logger_account.info(f'權限沒通過, 找不到url分類:userID: {userID},:url: {url}')
                    response = self.response_to_frontend(2)
                else: #gate1
                    is_public = self.check_url_is_public()
                    if is_public == 1:
                        response = self.response_to_frontend(0)
                        print('pass auth check')
                    elif is_public == 0:
                        # gate2
                        is_token_match = self.check_user_token(userID,token)
                        if is_token_match == 0: # 超過時效或沒登入的訪客進入該頁
                            logger_account.info(f'權限沒通過,超過時效或沒登入的訪客 :userID: {userID},:url: {url}')
                            response = self.response_to_frontend(3)
                        elif is_token_match == 2: #token不合. 被登出、須重登
                            logger_account.info(f'權限沒通過,token不合,需重登:userID: {userID},:url: {url}')
                            response = self.response_to_frontend(3)    
                        elif is_token_match == 1:
                            # gate3
                            self.get_user_group_and_permission_group(userID)
                            is_perm_match = self.check_auth_page_and_permission()
                            if is_perm_match == 0:
                                response = self.response_to_frontend(5)
                            elif is_perm_match == 1:
                                response = self.response_to_frontend(0)
                                print('pass auth check')
            #print(response)
            return(response)
        except Exception as e:
            logger_account.error(f'auth_tools 權限error: {e}')


