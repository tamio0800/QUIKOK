from django.db import models
from django.contrib.auth.models import User
class userToken(models.Model):
    authID = models.ForeignKey(User,on_delete=models.CASCADE)
    token = models.CharField(max_length=60) # 登入的時間+14天

class student_profile(models.Model):
    # 這是for存放一般會員/學生的額外資訊
    auth_id = models.IntegerField()  # 將用戶的auth_id聯動過來，方便進行query
    username = models.CharField(max_length = 150)
    password = models.CharField(max_length = 128)
    balance = models.IntegerField(default=0)  # 這個是帳戶餘額
    withholding_balance = models.IntegerField(default=0)  # 這個是帳戶預扣額度
    name = models.CharField(max_length = 40)
    nickname = models.CharField(max_length = 40)
    birth_date = models.DateField(null=True)
    is_male = models.BooleanField()
    intro = models.CharField(default='', max_length = 300, blank=True)  
    # 自我介紹，不要超過300個字元長，比老師長的緣故是比起老師，學生更需要詳細介紹自己的學習背景
    role = models.CharField(max_length = 40)
    mobile = models.CharField(max_length = 12)
    # picture_folder = models.ImageField(default = 'snapshop_default.png', blank =True)
    user_folder = models.CharField(max_length = 60) #該user最外層的資料夾路徑  從 picture_folder 改名,與老師的命名統一
    info_folder = models.CharField(max_length = 100)  # 資料夾路徑，存放個人檔案（暫不使用）
    thumbnail_dir = models.CharField(max_length = 150)
    update_someone_by_email = models.CharField(max_length = 405, blank=True)
    date_join = models.DateTimeField(auto_now_add=True)
    # 為了使回傳platform名稱而不是object
    def __str__(self):
        return self.username


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
    intro = models.CharField(max_length = 150)  # 簡短介紹，不要超過150個字元長
    mobile = models.CharField(max_length = 12)
    thumbnail_dir = models.CharField(max_length = 150) # 老師頭像完整路徑 thumbnail_dir
    user_folder = models.CharField(max_length = 60)  # 該user最外層的資料夾路徑
    info_folder = models.CharField(max_length = 100)  # 資料夾路徑，存放個人檔案目前暫沒使用
    tutor_experience = models.CharField(max_length = 12)  # 改成下拉式選單 五種分類
    subject_type = models.CharField(max_length = 400) # 科目名稱也可包含教課對象
    # id_cert = models.CharField(max_length = 150) 整合進下方的cert..裡面
    education_1 = models.CharField(max_length = 60, blank=True)
    education_2 = models.CharField(max_length = 60, blank=True)
    education_3 = models.CharField(max_length = 60, blank=True)
    cert_unapproved = models.CharField(max_length = 60) # 尚未審核通過的各類型證書/證明檔案指向資料夾位置
    cert_approved = models.CharField(max_length = 60) # 已審核通過的各類型證書/證明檔案指向資料夾位置
    # 四大類別的認證預設 false, 未認證
    id_approved = models.BooleanField(default = False)  #身分類別的認證勳章 實名認證
    education_approved = models.BooleanField(default = False)  #學歷類別的認證勳章 全部的學歷都有認證才通過
    work_approved = models.BooleanField(default = False)  #工作經歷類別的認證勳章:ex 某個厲害的公司,專案經驗
    other_approved = models.BooleanField(default = False)  #其他類別的認證勳章: ex:金色多益、奧林匹亞數學冠軍
    #occupation = models.CharField(max_length = 60, blank=True)
    company = models.CharField(max_length = 100, blank=True) # 公司與職位 原本分兩個但設計時做在一起了所以只留這個
    is_approved = models.BooleanField(default = False)  # 要讓陳先生看過/審核過
    date_join = models.DateTimeField(auto_now_add = True)
    special_exp = models.CharField(max_length = 300, blank=True)# 其他經歷或特殊專長


    def __str__(self):
        return self.username


class connects(models.Model):
    # 關係人table用來標註哪些人可以接收到哪些人的學習報告、資料等，有串聯的再於這個table中建立資料。
    username = models.CharField(max_length = 191)
    connected_user = models.CharField(max_length = 191)
    
    def __str__(self):
        return self.username


class dev_db(models.Model):
    username = models.CharField(max_length = 120)
    password = models.CharField(max_length = 100)
    name = models.CharField(max_length = 40)
    birth_date = models.DateField()
    is_male = models.BooleanField()
    date_join = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class general_available_time(models.Model):
    teacher_id =models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='general_time')        
    week=models.CharField(max_length=1)      #sun=6, mon=0, tue=1,...,
    time=models.CharField(max_length=133)       #Example:0,1,2,3,4,5,47
    # len(','.join([str(__ for _ in range(48)])) >> 133 
    def __str__(self):
        return self.user.username
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
    user=models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='specific_time')        
    date=models.DateField(max_length=20)        #Example:2020821
    time=models.CharField(max_length=133)       #Example:1,2,3,4,5,4
    def __str__(self):
        return self.user.username


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
    def __str__(self):
        return str(self.follower_auth_id)

class favorite_teachers(models.Model):
    # 這個暫時不會用到，先留著
    # 不特別限定老師或是學生使用
    follower_auth_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()
    def __str__(self):
        return str(self.follower_auth_id)