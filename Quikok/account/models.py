from django.db import models

class student_profile(models.Model):
    # 這是for存放一般會員/學生的額外資訊
    username = models.CharField(max_length = 150)
    password = models.CharField(max_length = 128)
    balance = models.IntegerField(default=0)  # 這個是帳戶餘額
    withholding_balance = models.IntegerField(default=0)  # 這個是帳戶預扣額度
    name = models.CharField(max_length = 40)
    nickname = models.CharField(max_length = 40)
    birth_date = models.DateField(null=True)
    is_male = models.BooleanField()
    intro = models.CharField(default='', max_length = 300)  
    # 自我介紹，不要超過300個字元長，比老師長的緣故是比起老師，學生更需要詳細介紹自己的學習北京
    role = models.CharField(max_length = 40)
    mobile = models.CharField(max_length = 12)
    # picture_folder = models.ImageField(default = 'snapshop_default.png', blank =True)
    picture_folder = models.CharField(max_length = 60)  # 改成資料夾路徑
    info_folder = models.CharField(max_length = 100)  # 資料夾路徑，存放個人檔案（暫不使用）
    update_someone_by_email = models.CharField(max_length = 405)
    date_join = models.DateTimeField(auto_now_add=True)
    # 為了使回傳platform名稱而不是object
    def __str__(self):
        return self.username


class teacher_profile(models.Model):
    # 這是for存放老師的額外資訊
    username = models.CharField(max_length = 150)
    password = models.CharField(max_length = 128)
    balance = models.IntegerField(default=0)  # 這個是帳戶餘額
    withholding_balance = models.IntegerField(default=0)  # 這個是帳戶預扣額度
    name = models.CharField(max_length = 40)
    nickname = models.CharField(max_length = 40)
    birth_date = models.DateField(null=True)
    is_male = models.BooleanField()
    intro = models.CharField(max_length = 150)  # 簡短介紹，不要超過150個字元長
    mobile = models.CharField(max_length = 12)
    # picture_folder = models.CharField(default = 'teacher_snapshop_default.png', blank =True) # 預設老師頭像
    picture_folder = models.CharField(max_length = 60)  # 改成資料夾路徑
    info_folder = models.CharField(max_length = 100)  # 資料夾路徑，存放個人檔案（暫不使用）
    tutor_experience = models.CharField(max_length = 12)  # 改成下拉式選單
    subject_type = models.CharField(max_length = 400) # 科目名稱也可包含教課對象
    # id_cert = models.CharField(max_length = 150) 整合進下方的cert..裡面
    education_1 = models.CharField(max_length = 60)
    education_2 = models.CharField(max_length = 60)
    education_3 = models.CharField(max_length = 60)
    cert_unapproved = models.CharField(max_length = 60) # 尚未審核通過的各類型證書/證明檔案指向資料夾位置
    cert_approved = models.CharField(max_length = 560) # 已審核通過的各類型證書/證明檔案指向資料夾位置
    id_approved = models.CharField(max_length = 60)  #身分類別的認證勳章
    education_approved = models.CharField(max_length = 60)  #學歷類別的認證勳章
    work_approved = models.CharField(max_length = 60)  #工作經歷類別的認證勳章
    other_approved = models.CharField(max_length = 60)  #其他類別的認證勳章
    occupation = models.CharField(max_length = 60)
    company = models.CharField(max_length = 60)
    date_join = models.DateTimeField(auto_now_add=True)

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
    user=models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='general_time')        
    week=models.CharField(max_length=10)        #mon=1,tus=2,...,sun=7
    time=models.CharField(max_length=100)       #Example:1,2,3,4,5,47
    def __str__(self):
        return self.user.username

class specific_available_time(models.Model):
    user=models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='specific_time')        
    date=models.CharField(max_length=20)        #Example:2020821
    time=models.CharField(max_length=100)       #Example:1,2,3,4,5,47
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

