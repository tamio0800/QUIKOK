# 跟權限確認有關係的功能
class auth_ckeck(**kwargs):
    def __init__(self):
        self.url_category_rules = self.create_url_rules()
         
        url = ''
        user_id = ''
    # read tabel
    def create_url_rules(self):
        # 目前有的各個網站的結構以及權限分類
        url_category_rules = {
            '老師會員中心': ('^/account/info/teacherS+', 'teacher'),
            '課程管理' : ('^/account/lessonS+','teacher'),
            '課程上架': ('^/lesson/ready/addS+','teacher'),
            '課程編輯': ('^/lesson/ready/edit/S+','teacher'),
            '課程預覽' : ('^/lesson/main/preview/S+','teacher'),
            '上課live_house' : ('', 'member_only'), # 還沒做到
            '聊天室主頁' : ('', 'member_only'), # 還沒做到
            '學生會員中心' : ('^/account/info/studentS+', 'student' ),
            '學生帳務中心' : ('', 'student'),
            '學習歷程': ('', 'student'),
            '方案購買': ('', 'student'),
            '課程預約': ('', 'student'),
            # 以下為公開頁面
            '首頁' : ('/home', 'public'),
            '課程搜尋頁' : ('^/lesson/search?q=S+', 'public'),
            '課程資訊頁' : ('^/lesson/main/view/S+', 'public'),
            '註冊新老師' : ('/account/register/teacherS+', 'public'),
            '註冊新學生' : ('^/account/register/studentS+', 'public')
        }
        return url_category_rules
    def check_url_belong_to_which_category(self, url):

        pass
    def write_into_db(self):
        from .models import auth_check
        for url_category_name, url_pattern in self.url_category_rules.items():
            auth_check.objects.update_or_create(
                category_name = url_category_name, 
                defaults = {'logout_time' : after_14days,
                            'token' : token
                                            },)

        for category in self.url_category_rules.keys():
            
#re.findall('^/account/info/teacherS+','/account/info/teacherS+')
    # 先拿 url 找 url的type
       # 用正則來處理前端給的url
       # 處理出來只有前面沒有後面
       # 再用處理出來的 url去db找 type
    # 如果 url_type == public:
        #直接 success有權限
    # else
    #   用 auth_id來看他有沒有資格看
    #