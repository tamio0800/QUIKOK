from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver



class user_token(models.Model):
    authID_object = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128) # hash密碼
    logout_time = models.CharField(max_length=60) # 登入的時間+14天
    def __str__(self):
        return str(self.id)
class auth_check(models.Model):
    url_auth_type = models.CharField(max_length = 30) 
    # teacher, student, member_only, public 
    # member_only的意思是只有會員才能看(例如聊天室沒有註冊、登入的訪客是無法看得)
    category_name = models.CharField(max_length = 30)
    # 網頁名稱例如: 老師會員中心,課程管理
    url_pattern = models.CharField(max_length = 300) 
    # 正在瀏覽的網址,不含流水號
    #auth_approve = models.BooleanField()

class student_profile(models.Model):
    # 這是for存放一般會員/學生的額外資訊
    auth_id = models.IntegerField()  # 將用戶的auth_id聯動過來，方便進行query
    username = models.CharField(max_length = 150)
    password = models.CharField(max_length = 128)
    balance = models.IntegerField(default=0)  # 帳戶餘額, = Q幣 -預扣額度
    withholding_balance = models.IntegerField(default=0)  # 帳戶預扣額度
    name = models.CharField(max_length = 40)
    nickname = models.CharField(max_length = 40)
    birth_date = models.DateField(blank=True, null=True)
    is_male = models.BooleanField()
    intro = models.TextField(default='', max_length = 300, blank=True, null=True)  
    # 自我介紹，不要超過300個字元長，比老師長的緣故是比起老師，學生更需要詳細介紹自己的學習背景
    role = models.CharField(max_length = 40)
    mobile = models.CharField(max_length = 12)
    # picture_folder = models.ImageField(default = 'snapshop_default.png', blank =True)
    user_folder = models.TextField(blank=True, null=True) #該user最外層的資料夾路徑  從 picture_folder 改名,與老師的命名統一
    info_folder = models.TextField(blank=True, null=True)  # 資料夾路徑，存放個人檔案（暫不使用）
    thumbnail_dir = models.TextField(blank=True, null=True)
    update_someone_by_email = models.CharField(max_length = 405, blank=True, null=True)
    bank_account_code = models.CharField(max_length=30, default='')
    bank_name = models.CharField(max_length=30, default='')
    bank_code = models.CharField(max_length=5, default='')
    date_join = models.DateTimeField(auto_now_add=True)
    # 為了使回傳platform名稱而不是object
    def __str__(self):
        return self.username

    class Meta:
        #ordering= ['-last_changed_time']  # 越新的會被呈現在越上面
        verbose_name = '學生個人資料'
        verbose_name_plural = '學生個人資料'


class student_review_aggregated_info(models.Model):
    '''
    用來存放、呈現學生的個人評價資訊
    '''
    student_auth_id = models.IntegerField(default=-1)  # -1 的話代表還沒有設定
    score_given_sum = models.PositiveIntegerField(default=0)  # 得到的評分加總總計
    reviewed_times = models.PositiveIntegerField(default=0)  # 得到的評分次數累計
    receiving_review_lesson_minutes_sum = models.PositiveIntegerField(default=0)  # 得到評分的那些課程的分鐘數總計
    is_student_late_for_lesson_times = models.PositiveIntegerField(default=0)  # 學生遲到次數
    is_student_being_frivolous_in_lesson_times = models.PositiveIntegerField(default=0)  # 學生不認真次數
    is_student_or_parents_not_friendly_times = models.PositiveIntegerField(default=0)  # 學生或家長不友善次數
    last_updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.student_auth_id)  # -- {str(self.score_given_to_times_mean)}

    # 下面是一些計算的數值

    def get_score_given_to_times_mean(self):
    # 得到的平均評分  (總分/被評分次數)，回傳到小數點後第一個數字
        if self.reviewed_times == 0:
            return -1  # -1代表目前沒有可用的值
        else:
            return round(
                self.score_given_sum / self.reviewed_times, 1)

    def get_on_time_index(self):
        '''準時到課指數，正常來說介於 0 - 100 之間'''
        if self.reviewed_times == 0:
            return -1  # -1代表目前沒有可用的值
        else:
            return 100.0 - round(
                self.is_student_late_for_lesson_times / self.reviewed_times * 100, 0)

    def get_studious_index(self):
        '''認真學習指數，正常來說介於 0 - 100 之間'''
        if self.reviewed_times == 0:
            return -1  # -1代表目前沒有可用的值
        else:
            return 100.0 - round(
                self.is_student_being_frivolous_in_lesson_times / self.reviewed_times * 100, 0)

    def get_friendly_index(self):
        '''友善指數，正常來說介於 0 - 100 之間'''
        if self.reviewed_times == 0:
            return -1  # -1代表目前沒有可用的值
        else:
            return 100.0 - round(
                self.is_student_or_parents_not_friendly_times / self.reviewed_times * 100, 0)

    class Meta:
        ordering= ['-last_updated_time']  # 越新的會被呈現在越上面
        verbose_name = '學生評價儀表板'
        verbose_name_plural = '學生評價儀表板'

class teacher_profile(models.Model):
    # 這是for存放老師的額外資訊
    auth_id = models.IntegerField()  # 將用戶的auth_id聯動過來，方便進行query
    username = models.CharField(max_length = 150) # 帳號
    password = models.CharField(max_length = 128)
    balance = models.IntegerField(default=0)  # 這個是帳戶餘額
    withholding_balance = models.IntegerField(default=0)  # 這個是帳戶預扣額度
    # future_balance = models.IntegerField(default=0) # 帳戶預進帳金額
    unearned_balance = models.IntegerField(default=0) # 帳戶預進帳金額，改成會計用語
    name = models.CharField(max_length = 40) #名字
    nickname = models.CharField(max_length = 40)
    birth_date = models.DateField(null=True)
    is_male = models.BooleanField()
    intro = models.TextField()  # 自我介紹
    mobile = models.CharField(max_length = 12)
    thumbnail_dir = models.TextField(blank=True, null=True) # 老師頭像完整路徑 thumbnail_dir
    user_folder = models.TextField(blank=True, null=True)  # 該user最外層的資料夾路徑
    info_folder = models.TextField(blank=True, null=True)  # 資料夾路徑，存放個人檔案目前暫沒使用
    tutor_experience = models.CharField(max_length = 12)  # 改成下拉式選單 五種分類
    subject_type = models.TextField(blank=True, null=True) # 科目名稱也可包含教課對象
    # id_cert = models.CharField(max_length = 150) 整合進下方的cert..裡面
    education_1 = models.CharField(max_length = 60)
    education_2 = models.CharField(max_length = 60, blank=True, null=True)
    education_3 = models.CharField(max_length = 60, blank=True, null=True)
    cert_unapproved = models.TextField(blank=True, null=True) # 尚未審核通過的各類型證書/證明檔案指向資料夾位置
    cert_approved = models.TextField(blank=True, null=True) # 已審核通過的各類型證書/證明檔案指向資料夾位置
    # 四大類別的認證預設 false, 未認證
    id_approved = models.BooleanField(default = False)  #身分類別的認證勳章 實名認證
    education_approved = models.BooleanField(default = False)  #學歷類別的認證勳章 全部的學歷都有認證才通過
    work_approved = models.BooleanField(default = False)  #工作經歷類別的認證勳章:ex 某個厲害的公司,專案經驗
    other_approved = models.BooleanField(default = False)  #其他類別的認證勳章: ex:金色多益、奧林匹亞數學冠軍
    #occupation = models.CharField(max_length = 60, blank=True)
    company = models.CharField(max_length = 100, blank=True, null=True) # 公司與職位 原本分兩個但設計時做在一起了所以只留這個
    is_approved = models.BooleanField(default = False)  # 要讓陳先生看過/審核過
    bank_account_code = models.CharField(max_length=30, default='')
    bank_name = models.CharField(max_length=30, default='')
    bank_code = models.CharField(max_length=5, default='')
    date_join = models.DateTimeField(auto_now_add = True)
    special_exp = models.TextField(blank=True, null=True)  # 其他經歷或特殊專長
    all_lesson_score_mean = models.FloatField(default=0.0)  # 全部課程分數平均
    total_number_of_remark = models.IntegerField(default=0) # 評分筆數
    def __str__(self):
        return self.username

    class Meta:
        #ordering= ['-last_changed_time']  # 越新的會被呈現在越上面
        verbose_name = '老師個人資料'
        verbose_name_plural = '老師個人資料'

class connects(models.Model):
    # 關係人table用來標註哪些人可以接收到哪些人的學習報告、資料等，有串聯的再於這個table中建立資料。
    username = models.CharField(max_length = 191)
    connected_user = models.CharField(max_length = 191)
    
    def __str__(self):
        return self.username


# from account.models import general_available_time as g
class general_available_time(models.Model):
    teacher_model = models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='general_time')        
    week=models.CharField(max_length=1)      #sun=6, mon=0, tue=1,...,
    time=models.CharField(max_length=250)       #Example:0,1,2,3,4,5...,47
    # 0 > 00:00 - 00:30
    # 1 > 00:30 - 01:00
    # .................
    # 46: 23:00 - 23:30
    # 47: 23:30 - 24:00
    # len(','.join([str(__ for _ in range(48)])) >> 133 
    def __str__(self):
        return self.teacher_model.username

    
# 就這個函式解釋一下怎麼與teacher_profile互相聯繫
# 這個table insert values後，會有一欄 user_id，
# 這個user_id就是該teacher在teacher_profile中的id；
# 假設我們在ORM中選了general_available_time某個row做為object(假設我們叫它gat)，
# 可以透過gat.user.the_column_you_want來呼叫該名老師的資訊。
# ===================
# 而在teacher_profile中，假設我們filter了一個物件叫做teacher1，
# 我們可以透過teacher1.general_time來取得該名老師對應的general_available_time物件。
# ===================
# 而如果是SQL，我們直接透過user_id，用join方式互串資訊就好囉。


class specific_available_time(models.Model):
    '''
    這是老師的詳細時段表，假設老師有空的時段如下:
    0| 2021-01-01| 1,2,3,4| False
    之後突然確認了 2021-01-01 時段 2 的預約，
    我們不需要回頭修改 id=0 的資料，直接新增如下即可:
    1| 2021-01-01| 2| True
    '''
    teacher_model=models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='specific_time') 
    date=models.DateField()    
    time=models.CharField(max_length=250)  #Example:1,2,3,4,5,4
    is_occupied=models.BooleanField(default=False)  # 該時段是否已經被預訂了  
    def __str__(self):
        return self.teacher_model.username

class student_studying_history(models.Model):
    # 這個是學生的學習歷程紀錄，先留著之後再完善
    user=models.ForeignKey(student_profile, on_delete=models.CASCADE, related_name='studying_history')
    def __str__(self):
        return self.user.username


class teacher_teaching_history(models.Model):
    # 這個是老師的授課歷程紀錄，先留著之後再完善
    user=models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='teaching_history')
    def __str__(self):
        return self.user.username


class favorite_lessons(models.Model):
    # 不特別限定老師或是學生使用
    follower_auth_id = models.IntegerField()
    lesson_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()  # 這個用來表示這門課是誰開的
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.follower_auth_id)

class favorite_teachers(models.Model):
    # 這個暫時不會用到，先留著
    # 不特別限定老師或是學生使用
    follower_auth_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()
    def __str__(self):
        return str(self.follower_auth_id)


class feedback(models.Model):
    # 用來儲存user的問題反應
    who_are_you = models.CharField(max_length=40)
    contact = models.CharField(max_length=150)
    problem = models.TextField()
    on_which_page = models.TextField()
    is_signed_in = models.BooleanField()
    # user 回報問題時是否有登入
    is_replied = models.BooleanField(default=False)
    # 回覆了沒
    is_resolved = models.BooleanField(default=False)
    # 解決了沒
    created_time = models.DateTimeField(auto_now=True)
    last_edited_time = models.DateTimeField(auto_now_add=True)
    # 可以用來衡量問題回覆、解決的時間長度
    def __str__(self):
        return str(self.id)

    
@receiver(post_save, sender=student_profile)
def when_lesson_completed_notification_sent_by_teacher(sender, instance:student_profile, created, **kwargs):
    # 代表student_profile建立了新學生資料，這時候我們一起幫他建立對應的評價儀表板
    if created:
        # 代表是新建立
        student_review_aggregated_info.objects.create(
            student_auth_id = instance.auth_id,
        ).save()

        
