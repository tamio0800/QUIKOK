from django.db import models
from django.contrib.auth.models import User


class user_profile(models.Model):
    # 這是for存放一般會員/學生的額外資訊
    username = models.CharField(max_length = 191)  # 這個是要跟user table做join的key值
    nickname = models.CharField(max_length = 40)
    birth_date = models.DateField()
    is_male = models.BooleanField()
    role = models.CharField(max_length = 40)
    mobile = models.CharField(max_length = 12)
    picture_folder = models.CharField(max_length = 150)
    tracking_mobile = models.CharField(max_length = 130)  
    update_someone_by_email = models.CharField(max_length = 405)
    update_someone_by_mobile = models.CharField(max_length = 65)

    # 為了使回傳platform名稱而不是object
    def __str__(self):
        return self.username


class vendor_profile(models.Model):
    # 這是for存放老師的額外資訊
    username = models.CharField(max_length = 191)  # 這個是要跟user table做join的key值
    nickname = models.CharField(max_length = 40)
    birth_date = models.DateField()
    is_male = models.BooleanField()
    intro = models.CharField(max_length = 300)  # 簡短介紹，不要超過300個字元長(2/漢字)
    mobile = models.CharField(max_length = 12)
    picture_folder = models.CharField(max_length = 150)
    tutor_exp_in_years = models.FloatField(default=0.0)
    student_type = models.CharField(max_length = 400)
    subject_type = models.CharField(max_length = 400)
    id_cert = models.CharField(max_length = 150)
    education_1 = models.CharField(max_length = 60)
    education_2 = models.CharField(max_length = 60)
    education_3 = models.CharField(max_length = 60)
    education_cert_1 = models.CharField(max_length = 150)
    education_cert_2 = models.CharField(max_length = 150)
    education_cert_3 = models.CharField(max_length = 150)
    occupation = models.CharField(max_length = 60)
    company = models.CharField(max_length = 60)
    occupation_cert = models.CharField(max_length = 150)

    def __str__(self):
        return self.username


class connects(models.Model):
    # 關係人table用來標註哪些人可以接收到哪些人的學習報告、資料等，有串聯的再於這個table中建立資料。
    username = models.CharField(max_length = 191)
    connected_user = models.CharField(max_length = 191)
    
    def __str__(self):
        return self.username