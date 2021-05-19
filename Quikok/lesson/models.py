from django.db import models
from account.models import teacher_profile, student_profile
from datetime import timedelta, date as date_function
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from handy_functions import get_lesson_s_best_sale, get_teacher_s_best_education_and_working_experience
from handy_functions import handy_round

import logging
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        

class lesson_info(models.Model): # 0903架構還沒想完整先把確定有的東西填入
    # 每堂課程會有自己的unique id，我們用這個來辨識、串連課程 09/25 討論後認為先用內建的id就好
    # lesson_id = models.CharField(max_length = 40) 
    teacher = models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='teacher_of_the_lesson')
    big_title = models.CharField(max_length = 10, default="", blank=True)  # 背景圖片的大標題
    little_title = models.CharField(max_length = 10, default="", blank=True)  # 背景圖片的小標題
    title_color = models.CharField(max_length = 7) # 標題顏色 以色碼存入，  >> #\d{6}
    background_picture_code = models.IntegerField()
    # 這個用來儲存user選擇了什麼樣的上架背景圖，舉例來說99代表user自己上傳的圖，這時我們要找到對應的路徑回傳給前端；
    # 如果今天這個值是1、2、3之類的Quikok預設圖片，那我們直接回傳代號給前端即可。
    background_picture_path = models.TextField(blank=True) # 指向上傳圖的路徑
    lesson_title = models.CharField(max_length = 14) # 課程的名稱
    price_per_hour = models.IntegerField()  # 該門課程的鐘點費
    lesson_has_one_hour_package = models.BooleanField(default=False)  # 該門課程是否可以單堂出售
    trial_class_price = models.IntegerField(default=-999)  # 該門課程的試上鐘點費, 若無試教則為 -999
    discount_price = models.CharField(max_length=30, default="", blank=True) # 優惠折數
    # discount_price說明
    # 假設老師勾選了方案一 & 方案二 & 方案三，內容各自為：
    # 一次購買「10」小時，提供總價「95」%優惠價..
    # 一次購買「20」小時，提供總價「80」%優惠價..
    # 一次購買「30」小時，提供總價「70」%優惠價..
    # 此時 discount_price >> "10:95;20:80;30:70;"。
    # 若只勾選方案一，則為：
    # discount_price >> "10:95;"
    highlight_1 = models.CharField(max_length=10, default="", blank=True)  # 亮點介紹1，不要超過10個字元長
    highlight_2 = models.CharField(max_length=10, default="", blank=True)  # 亮點介紹2，不要超過10個字元長
    highlight_3 = models.CharField(max_length=10, default="", blank=True)  # 亮點介紹3，不要超過10個字元長
    lesson_intro = models.TextField(blank=True, null=True, default="")
    # lesson_intro = models.CharField(blank=True, max_length=300)
    # 課程詳細介紹，不超過300長度
    how_does_lesson_go = models.TextField(blank=True, null=True, default="")
    # 課程方式/教學方式，舉例來說：「本堂課前十分鐘小考，測驗上次的內容吸收程度，
    # 接著正式上課兩小時，最後15分鐘溫習。」
    is_this_lesson_online_or_offline = models.CharField(max_length=10, default='online')
    # 是線上課程(online)或是實體課程(offline)
    target_students = models.TextField(blank=True, null=True, default="") # 授課對象
    lesson_remarks = models.TextField(blank=True, null=True, default="") # 備註，目前是用來儲存「給學生的注意事項」
    # lesson_background_folder = models.CharField(max_length = 80)# 該課程背景圖片指向的資料夾 可選預設或上傳
    # lesson_picture_folder = models.CharField(max_length = 80) # 目前版本用不到本col 如果目前版本用不到本col有相關圖片，可以儲存在這個資料夾中
    syllabus = models.TextField(blank=True, null=True, default="") 
    # 存放課程的綱要或架構，預計會以html的方式傳遞/儲存 格式:大標/小標:內容; 
    # lesson_appendix_folder = models.CharField(max_length = 80)
    # 目前版本用不到本col 如果將來有相關附件，可以儲存在這個資料夾中
    # 這裡還要記得把老師的有空時段連過來
    # is_approved = models.BooleanField(default=False)
    lesson_attributes = models.TextField(blank = True, default="")
    # 這個是放課程的標籤，一開始先人工(老師)給，之後再交給機器學習模型來判斷
    hidden_lesson_attributes = models.TextField(blank = True, default="")
    # 將老師給定的標籤，加上我們自己分析課程資訊的結果後，放在這裡面，當作是最終的標籤，避免讓老師改到
    lesson_avg_score = models.FloatField(default = 0.0) # 這個是平均評分，每次評分表一更新這裡也會連動更新
    lesson_reviewed_times = models.IntegerField(default = 0) # 這個是課程被評分過幾次的統計
    created_time = models.DateTimeField(auto_now_add=True)
    edited_time = models.DateTimeField(auto_now=True)
    lesson_ranking_score = models.IntegerField(default = 0) # 這個是課程排序的依據分數
    selling_status = models.CharField(max_length = 20)
    # 販售狀態 >>
    #   草稿: draft, 上架: selling, 沒上架: notSelling, 刪除: donotShow
    def __str__(self):
        return f"課程({self.id}): {self.lesson_title}, 由{self.teacher.nickname}老師({self.teacher.auth_id})所創立"

    class Meta:
        verbose_name = '課程資訊-詳細'
        verbose_name_plural = '課程資訊-詳細'
        ordering = ['-created_time']


class lesson_card(models.Model):
    # 這個table用來儲存課程小卡的資訊，原因是當我們課程變多的時候，
    # 要即時組合老師、課程、評價資訊會需要大量的運算，不如多建立一個table，
    # 之後直接query就好。
    corresponding_lesson_id = models.IntegerField()  # 所對應的課程id
    teacher_thumbnail_path = models.TextField(blank=True, null=True)  # 老師的大頭照路徑
    teacher_nickname = models.CharField(max_length = 40)
    teacher_auth_id = models.IntegerField()
    is_this_teacher_male = models.BooleanField(default=True)
    is_this_lesson_online_or_offline = models.CharField(max_length=10, default='online') # 是線上課程(online)或是實體課程(offline)
    big_title = models.CharField(max_length = 10)  # 背景圖片的大標題
    little_title = models.CharField(max_length = 10)  # 背景圖片的小標題
    title_color = models.CharField(max_length = 7)    
    background_picture_code = models.IntegerField()
    background_picture_path = models.TextField(blank=True, null=True) # 指向上傳圖的路徑
    lesson_title = models.CharField(max_length = 14) # 課程的名稱
    highlight_1 = models.CharField(max_length = 10)  # 亮點介紹1，不要超過10個字元長
    highlight_2 = models.CharField(max_length = 10)  # 亮點介紹2，不要超過10個字元長
    highlight_3 = models.CharField(max_length = 10)  # 亮點介紹3，不要超過10個字元長
    price_per_hour = models.IntegerField()  # 該門課程的鐘點費
    best_sale = models.CharField(max_length = 20) # 用來吸引人的最優惠折價標語
    education = models.CharField(max_length = 60, blank=True, null=True)  # 最高學歷說明
    education_is_approved = models.BooleanField()
    working_experience = models.CharField(max_length = 100, blank=True, null=True)  # 經歷說明
    working_experience_is_approved = models.BooleanField()
    lesson_avg_score = models.FloatField(default = 0.0) # 這個是平均評分，每次評分表一更新這裡也會連動更新
    lesson_reviewed_times = models.IntegerField(default = 0) # 這個是課程被評分過幾次的統計
    lesson_ranking_score = models.IntegerField(default = 0) # 這個是課程排序的依據分數
  
    def __str__(self):
        return f"{self.teacher_nickname} 老師開設的 {self.lesson_title} 課程"

    class Meta:
        verbose_name = '課程資訊-小卡'
        verbose_name_plural = '課程資訊-小卡'


class lesson_reviews_from_students(models.Model):
    '''
    這個是讓學生在課後給老師/課程評價的 TABLE
    '''
    corresponding_lesson_id = models.IntegerField()  # 所對應的課程id
    corresponding_lesson_booking_info_id = models.IntegerField()  # 所對應的課程預約id
    corresponding_lesson_completed_record_id = models.IntegerField()  # 所對應的完課紀錄id
    student_auth_id = models.IntegerField()  # 上課學生的auth_id，也是留下評論的人
    teacher_auth_id = models.IntegerField()  # 上課老師的auth_id，是此次被評論的對象
    score_given = models.IntegerField(blank=True, null=True) # 對於本次課程綜合的評分，介於1~5分之間
    is_teacher_late_for_lesson = models.BooleanField(blank=True, null=True) # 老師是否有遲到
    is_teacher_frivolous_in_lesson = models.BooleanField(blank=True, null=True) # 老師是否不認真教學
    is_teacher_incapable = models.BooleanField(blank=True, null=True) # 老師是否不勝任這門課、教太廢
    remark_given = models.TextField(blank=True, null=True)  # 這個是評語
    # picture_folder = models.TextField() # 加上真的有上課的圖以資證明（學蝦皮
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"課程({str(self.corresponding_lesson_id)}), 預約({str(self.corresponding_lesson_booking_info_id)}), 完課({str(self.corresponding_lesson_completed_record_id)})\
            學生({str(self.student_auth_id)})對老師({str(self.teacher_auth_id)})。"

    class Meta:
        verbose_name = '評價-學生對老師/課程'
        verbose_name_plural = '評價-學生對老師/課程'
        ordering = ['-created_time']


class student_reviews_from_teachers(models.Model):
    '''
    這個是讓老師在課後給評價的 TABLE
    '''
    corresponding_lesson_id = models.IntegerField()  # 所對應的課程id
    corresponding_lesson_booking_info_id = models.IntegerField()  # 所對應的課程預約id
    corresponding_lesson_completed_record_id = models.IntegerField()  # 所對應的完課紀錄id
    student_auth_id = models.IntegerField()  # 上課學生的auth_id，是此次被評論的對象
    teacher_auth_id = models.IntegerField()  # 上課老師的auth_id，是留下評論的人
    score_given = models.PositiveIntegerField(blank=True, null=True) # 對於本次課程的綜合評分，介於1~5分之間
    is_student_late_for_lesson = models.BooleanField(blank=True, null=True) # 學生是否有遲到
    is_student_frivolous_in_lesson = models.BooleanField(blank=True, null=True) # 學生是否不認真
    is_student_or_parents_not_friendly = models.BooleanField(blank=True, null=True) # 學生或家長是否不友善
    remark_given = models.TextField(blank=True, null=True)  # 這個是評語
    # picture_folder = models.TextField() # 加上真的有上課的圖以資證明（學蝦皮
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"課程({str(self.corresponding_lesson_id)}), 預約({str(self.corresponding_lesson_booking_info_id)}), 完課({str(self.corresponding_lesson_completed_record_id)})\
            老師({str(self.teacher_auth_id)})對學生({str(self.student_auth_id)})。"

    class Meta:
        verbose_name = '評價-老師對學生'
        verbose_name_plural = '評價-老師對學生'
        ordering = ['-created_time']


class lesson_booking_info(models.Model): 
    '''課程的預約管理table，這個model是用來管理「每一則booking」的狀態與profile'''
    # student_remaining_minutes_of_each_purchased_lesson_set_id= models.IntegerField()
    # 對應的訂單所剩的時數
    lesson_id = models.IntegerField()  # 對應的課程id
    # student_remaining_minutes_of_each_purchased_lesson_set_ids = models.CharField(default='', max_length=20)
    # 對應的 student_remaining_minutes_of_each_purchased_lesson_set id 們
    # 之所以 default = '' ，因為這樣子在我先前寫的測試中(不會用到這個欄位)就不會有一大堆衝突了QQ
    # 因為一則購買的方案可以用來做很多預約（多對一），
    # 反之方案快用完的時候也可能兩三個購買方案才能用來做一次大量預約（一對多），
    # 所以這裡使用 string 來做儲存，會長得類似： "9,10,11" or "3" 這樣子，
    # 當要 query 對應的 queryset 時可以這樣做  
    # student_remaining_minutes_of_each_purchased_lesson_set_ids 先簡寫為 srm_ids
    #   1. 
    #         for each_id in lesson_booking_info.objects.filter(id=1).srm_ids.split(','):
    #            student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(id=each_id)
    #            ...
    #  <<<<<>>>>> OR <<<<<>>>>>
    #   2.
    #         student_remaining_minutes_of_each_purchased_lesson_set.objects.filter(
    #               id__in = lesson_booking_info.objects.filter(id=1).srm_ids.split(',')
    #         )
    teacher_auth_id = models.IntegerField()
    student_auth_id = models.IntegerField()
    parent_auth_id = models.IntegerField(default=-1)
    booked_by = models.CharField(max_length = 20)  # teacher or student or parent
    last_changed_by = models.CharField(max_length = 20)  # teacher or student or parent
    booking_set_id = models.IntegerField()
    # 預約使用的是該課程的哪一個方案（ID），這個之後會另外建立一個「每個課程的方案table」來做串連。
    remaining_minutes = models.IntegerField()
    # 這個指的是假設這門課準時上完，則學生還有多少時數，用意是讓老師知道萬一超時會不會多拿到錢
    booking_date_and_time = models.CharField(max_length=400)  
    # Example: 2020-08-21:1,2,3,4; 之類的
    booking_start_datetime = models.DateTimeField()
    booking_status = models.CharField(max_length = 60)  
    # to_be_confirmed  >>  發送預約，但是還未經對方確認 
    # confirmed  >>  發送的預約已經被對方確認
    # canceled  >>  預約被取消（無須對方同意）
    # finished  >> 課程已經結束，並且雙方都確認時數，是真正的finished
    #   下面還包含此兩者狀態
    #       student_not_yet_confirmed >> 也包含在finished，代表學生尚未確認時數
    #       quikok_dealing_for_student_disagreed >> 客服正在處理學生反應時數不正確
    remark = models.CharField(max_length=40, default='')
    # 把課程預約的註記擺在這邊好了，直接從這裡call，而不是在搜尋歷史資料時及時產出  
    created_time = models.DateTimeField(auto_now_add=True)
    last_changed_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"課程({self.lesson_id})的預約({self.id})：學生({self.student_auth_id})預約老師({self.teacher_auth_id})的課程({self.lesson_id})的方案({self.booking_set_id})。 目前狀態:{self.booking_status}; 最後更改時間:{self.last_changed_time.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_booking_date(self):
        # 回傳這次的預約日期
        return date_function([int(_) for _ in self.booking_date_and_time.split(':')[0].split('-')])

    def get_booking_time_in_minutes(self):
        # 回傳這次的預約總計多少分鐘
        return int(len(self.booking_date_and_time[:-1].split(':')[1].split(','))) * 30

    class Meta:
        verbose_name = '預約-課程預約資訊'
        verbose_name_plural = '預約-課程預約資訊'
        ordering = ['-created_time']


# 上課與完課紀錄
class lesson_completed_record(models.Model):
    lesson_booking_info_id = models.IntegerField()  # 對應的課程id
    student_remaining_minutes_of_each_purchased_lesson_set_id= models.IntegerField()
    # 對應的訂單所剩的時數
    teacher_auth_id = models.IntegerField()
    student_auth_id = models.IntegerField()
    booking_time_in_minutes = models.IntegerField() # 預估上課時間時數,單位分鐘,是用預約的時間計算的
    tuition_fee = models.IntegerField(null=True) 
    # 根據老師宣稱的上課時數計算出來該堂課的費用, 這個費用當雙方都同意時,會撥入老師 balance
    # 萬一學生不同意時, edony也可以改這格的金額, 並註記到remark
    teacher_declared_start_time = models.DateTimeField()
    # 老師號稱的上課時間,單位是分鐘,10分鐘一跳
    teacher_declared_end_time = models.DateTimeField()
    # 老師號稱的下課時數, 單位是分鐘, 10分鐘一跳
    teacher_declared_time_in_minutes = models.IntegerField() 
    # 老師號稱的開課時間總時數,可能課程實際時間會比原本預約時有所增減(單位是分鐘)
    # teacher_declared_teaching_fee = models.IntegerField()
    # 老師號稱的應付老師金額  << 這個有需要嗎??  反正只是扣時數而已說
    # teaching_status = models.CharField(max_length = 20)  
    # 這個欄位好像用不到還沒上課 unprocess, 已完課 over or canceled
    is_student_disagree_with_teacher_s_declared_time = models.BooleanField(default= False)
    # 學生是否反應老師宣稱的時數有問題
    is_student_confirmed = models.BooleanField(default= False)
    # default=False,當學生確認時數後改為True, 萬一需要協調時數用
    student_confirmed_deadline = models.DateField()
    # 這個的作用是，假設學生遲遲不確認，我們還是要在某個時段過後撥錢給老師，
    # 目前先預設3天? 也就是說，當在老師發送確認訊息後的3天後，假設學生還沒確認也沒申訴，
    # 則我們將直接撥款給老師
    confirmed_by_quikok = models.BooleanField(default= False)
    # 萬一學生遲遲不確認，要由我們自動確認的話，最好也做個註記
    quikok_remarks = models.TextField(default="", blank=True, null=True)
    # 萬一未來需要協調時，這個欄位可以讓我們做一些協調紀錄/處理經過
    created_time = models.DateTimeField(auto_now_add=True)
    last_changed_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        lesson_id = lesson_booking_info.objects.get(id=self.lesson_booking_info_id).lesson_id
        return f"課程({lesson_id})的預約({self.lesson_booking_info_id})已被老師({self.teacher_auth_id})通報完課。 學生({self.student_auth_id})是否同意: {self.is_student_confirmed}、是否(曾)申訴: {self.is_student_disagree_with_teacher_s_declared_time}。 是否由Quikok自動確認: {self.confirmed_by_quikok}"
        # return f"課程的預約({self.lesson_booking_info_id})已被老師({self.teacher_auth_id})通報完課。 學生({self.student_auth_id})是否同意: {self.is_student_confirmed}、是否(曾)申訴: {self.is_student_disagree_with_teacher_s_declared_time}。 是否由Quikok自動確認: {self.confirmed_by_quikok}"
    class Meta:
        verbose_name = '預約-完課紀錄'
        verbose_name_plural = '預約-完課紀錄'
        ordering = ['-created_time']
        

class lesson_sales_sets(models.Model):
    '''
    課程的方案table，這個只能一直往下疊加狀態，
    原因是不能讓之前購買課程的user受到影響，舉例來說： 
        1. 學生s購買了老師t的「30小時：優惠7折方案」 
        2. 老師t將「30小時：優惠7折方案」改成 >> 「30小時：優惠9折方案」 
        3. 但因為學生s之前已經付款成功了，這時候不應該改變他已購買方案的狀態。

    >> 應該要在課程建立、編輯時同步寫入。
    '''
    lesson_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()
    price_per_hour = models.IntegerField()  # 老師原始的鐘點費
    price_per_10_minutes = models.FloatField(null=True)  
    # 原始鐘點費除以6,會以這個金額計算完課撥款費用,固定存到小數第5位<由view算
    sales_set = models.CharField(max_length = 20)
    #  試課優惠：'trial'
    #  單堂原價：'no_discount'
    #  30小時7折優惠：'30:70'
    total_hours_of_the_sales_set = models.IntegerField()  # 該方案的總時數(小時)
    # 如果是試教的話，先給值1
    total_amount_of_the_sales_set = models.IntegerField()  # 該方案的總價
    price_per_hour_after_discount = models.IntegerField()  # 折扣後，該方案的鐘點費
    selling_volume = models.IntegerField(default=0)  # 銷售的總量
    taking_lesson_volume = models.IntegerField(default=0)  # 上課中的總量(曾預約成功過)
    fulfilled_volume = models.IntegerField(default=0)  # 已完成課程的總量
    created_time = models.DateTimeField(auto_now_add=True)
    last_sold_time = models.DateTimeField(auto_now=True)
    is_open = models.BooleanField(default=True) 

    #是否為目前使用中的方案, 是的話才可選
    def __str__(self):
        return f"課程({self.lesson_id})：{self.sales_set} 方案，總價{self.total_amount_of_the_sales_set}元。 啟用中：{self.is_open}"
    
    class Meta:
        verbose_name = '課程方案資訊'
        verbose_name_plural = '課程方案資訊'
        ordering = ['-created_time']


class lesson_info_for_users_not_signed_up(models.Model): 
    # 因為有一個先期導入版本，我們利用一個暫存的lesson_info先存放這些資訊，
    # 差別是 >> 
        # 1.「teacher」這個foreign key 被 dummy_teacher_id (char) 取代 
        # 2. 將一些一定不會有的資訊column刪掉留待用戶註冊後再用正式table加上去，像是：
            # 課程評分、瀏覽人數、販售狀態、之類的～
    dummy_teacher_id = models.CharField(max_length=100)
    big_title = models.CharField(max_length = 10)  # 背景圖片的大標題
    little_title = models.CharField(max_length = 10)  # 背景圖片的小標題
    title_color = models.CharField(max_length = 7) # 標題顏色 以色碼存入，  >> #\d{6}
    background_picture_code = models.IntegerField()
    # 這個用來儲存user選擇了什麼樣的上架背景圖，舉例來說99代表user自己上傳的圖，這時我們要找到對應的路徑回傳給前端；
    # 如果今天這個值是1、2、3之類的Quikok預設圖片，那我們直接回傳代號給前端即可。
    background_picture_path = models.TextField(blank=True) # 指向上傳圖的路徑
    lesson_title = models.CharField(max_length = 14) # 課程的名稱
    price_per_hour = models.IntegerField()  # 該門課程的鐘點費
    lesson_has_one_hour_package = models.BooleanField()  # 該門課程是否可以單堂出售
    trial_class_price = models.IntegerField()  # 該門課程的試上鐘點費
    highlight_1 = models.CharField(max_length = 10)  # 亮點介紹1，不要超過10個字元長
    highlight_2 = models.CharField(max_length = 10)  # 亮點介紹2，不要超過10個字元長
    highlight_3 = models.CharField(max_length = 10)  # 亮點介紹3，不要超過10個字元長
    discount_price = models.CharField(max_length = 30) # 優惠折數
    lesson_intro = models.TextField(blank=True, null=True)
    how_does_lesson_go = models.TextField(blank=True, null=True)
    # 課程方式/教學方式，舉例來說：「本堂課前十分鐘小考，測驗上次的內容吸收程度，
    # 接著正式上課兩小時，最後15分鐘溫習。」
    target_students = models.TextField(blank=True, null=True) # 授課對象
    lesson_remarks = models.TextField(blank=True, null=True) # 備註，目前是用來儲存「給學生的注意事項」
    syllabus = models.TextField(blank=True, null=True) 
    # 存放課程的綱要或架構，預計會以html的方式傳遞/儲存 格式:大標/小標:內容; 
    # 目前版本用不到本col 如果將來有相關附件，可以儲存在這個資料夾中
    # 這裡還要記得把老師的有空時段連過來
    lesson_attributes = models.TextField(blank = True)  
    # 這個是放課程的標籤，一開始先人工(老師)給，之後再交給機器學習模型來判斷
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.lesson_title
        # 理論上一個老師在這張table只會有一個row的資料，所以這樣寫比較好看



'''
下面用來寫一些modles的函式
'''
def extract_subject_attributes_from_lesson(**kwargs):
    '''
    從lesson_id獲取對應的課程資訊後，將如標題、小標題、內容、說明等等的資訊整合起來，
    利用人工的方式比對某個課程類別是不是被包含在該課程中；
    範例如：
        Input: 2
        Output: "數學,英文,國文"
    未來再改用NLP模型判斷。
    '''
    mapping_dict = {
        '英文': ('英語', '英文', '美語', '美式發音', '英式發音', '多益', '托福', '雅思',
            'english', 'ielts', 'tofel', 'toeic'),
        '國文': ('國文', '國語'),
        '數學': ('數學', '數理', '算數', 'math'),
        '物理': ('物理', '數理'),
        '化學': ('化學', '化工'),
        '留學相關': ('ielts', '雅思', 'tofel', '托福', 'sat', 'act', 'ap', 'ib', 'ssat', 'psat', 'ibdp'),
        '語言教學': ('英文', '外語', '美語', '英語', '韓語', '韓文', '日文', '日語', 
            '越南文', '越南語', '西班牙語', '西班牙文', '法語', '法文', '德語', '德文'),
        '學科教育': ('數學', '物理', '國文', '國語', '化學', '理化', '自然', '生物'),
        '職場技能': ('excel', 'vba', '文書', '行政', '自動化', '禮節', '商務')
    }  # 都沒有的話就 其他類型
    # lesson_object = lesson_info.objects.get(id=lesson_id)
    # 確實有該門課程
    big_title = kwargs['big_title']
    little_title = kwargs['little_title']
    lesson_title = kwargs['lesson_title']
    highlight_1 = kwargs['highlight_1']
    highlight_2 = kwargs['highlight_2']
    highlight_3 = kwargs['highlight_3']
    lesson_intro = kwargs['lesson_intro']
    how_does_lesson_go = kwargs['how_does_lesson_go']
    lesson_remarks = kwargs['lesson_remarks']
    lesson_attributes = \
        kwargs['lesson_attributes'].replace('＃', '').replace('　', ' ').replace('#', '').replace('\r', ',').replace('\n', ',')
    aggregated_string = \
        big_title + ',' + little_title + ',' + lesson_title + ',' + highlight_1 + \
        ',' + highlight_2 + ',' + highlight_3 + ',' + lesson_intro + ',' + how_does_lesson_go + \
        ',' + lesson_remarks + ',' + lesson_attributes
    aggregated_string = aggregated_string.lower()
    # print(f"extract_subject_attributes_from_lesson  {aggregated_string}")
    # 轉成全小寫方便比對
    mapped_subjects = list()
    # print(mapping_dict.items())
    for k, v in mapping_dict.items():
        for each_v in v:
            if each_v in aggregated_string:
                print(k, each_v)
                mapped_subjects.append(k)
                break
    if len(mapped_subjects) == 0:
        mapped_subjects.append('其他類型')
    
    for _ in lesson_attributes.split():
        if _ not in mapped_subjects:
            mapped_subjects.append(_)

    return ','.join(sorted(mapped_subjects))


'''
下面用來寫signal監聽特定 TABLES 是否有改動，而進行對應動作的機制
'''
  
@receiver(post_save, sender=lesson_info)
def when_lesson_info_changed(sender, instance:lesson_info, created, **kwargs):
    '''
    1. 當課程新建立或是編輯的時候，重新萃取一下課程的特徵/屬性，並儲存到 hidden_lesson_attributes 欄位。
    2. 當 lesson_info 這個 table 有新建課程或是編輯課程的動作時，要同步對課程小卡進行更新。
    '''

    # = = = = = = = = 這裡用來執行 同步對課程小卡進行更新 = = = = = = = = 
    first_exp, second_exp, is_first_exp_approved, is_second_exp_approved = \
        get_teacher_s_best_education_and_working_experience(instance.teacher)

    if instance.background_picture_path != '':
        # 用戶有上傳課程背景圖，需要儲存對應的小卡縮圖
        background_picture_path_for_lesson_cards = \
            instance.background_picture_path.replace(
                'customized_lesson_background',
                'customized_lesson_background_for_cards')
    else:
        background_picture_path_for_lesson_cards = ''

    if created:
        # 代表新建立了一門課程，此時要建立課程小卡的資料
        lesson_card.objects.create(
            corresponding_lesson_id = instance.id,
            teacher_thumbnail_path = instance.teacher.thumbnail_dir,
            teacher_nickname = instance.teacher.nickname,
            teacher_auth_id = instance.teacher.auth_id,
            is_this_teacher_male = instance.teacher.is_male,
            is_this_lesson_online_or_offline = instance.is_this_lesson_online_or_offline,
            big_title = instance.big_title,
            little_title = instance.little_title,
            title_color = instance.title_color,
            background_picture_code = instance.background_picture_code,
            background_picture_path = background_picture_path_for_lesson_cards,
            lesson_title = instance.lesson_title,
            highlight_1 = instance.highlight_1,
            highlight_2 = instance.highlight_2,
            highlight_3 = instance.highlight_3,
            price_per_hour = instance.price_per_hour,
            best_sale = get_lesson_s_best_sale(instance),
            education = first_exp,
            education_is_approved = is_first_exp_approved,
            working_experience = second_exp,
            working_experience_is_approved = is_second_exp_approved,
            lesson_avg_score = 0.0,
            lesson_reviewed_times = 0,
            lesson_ranking_score = instance.lesson_ranking_score)
        logging.info(f'Created lesson_card object after creating a lesson ({instance.lesson_title}).')
    else:
        # 代表編輯了一門課程，此時要同步更新課程小卡的資料，只要更新跟課程有關的即可
        # 先找到對應的小卡物件
        lesson_card_objects = lesson_card.objects.get(corresponding_lesson_id=instance.id)
        lesson_card_objects.is_this_lesson_online_or_offline = instance.is_this_lesson_online_or_offline
        lesson_card_objects.big_title = instance.big_title
        lesson_card_objects.little_title = instance.little_title
        lesson_card_objects.title_color = instance.title_color
        lesson_card_objects.background_picture_code = instance.background_picture_code
        lesson_card_objects.background_picture_path = background_picture_path_for_lesson_cards
        lesson_card_objects.lesson_title = instance.lesson_title
        lesson_card_objects.highlight_1 = instance.highlight_1
        lesson_card_objects.highlight_2 = instance.highlight_2
        lesson_card_objects.highlight_3 = instance.highlight_3
        lesson_card_objects.price_per_hour = instance.price_per_hour
        lesson_card_objects.best_sale = get_lesson_s_best_sale(instance)
        lesson_card_objects.education = first_exp
        lesson_card_objects.education_is_approved = is_first_exp_approved
        lesson_card_objects.working_experience = second_exp
        lesson_card_objects.working_experience_is_approved = is_second_exp_approved
        lesson_card_objects.lesson_ranking_score = instance.lesson_ranking_score
        lesson_card_objects.save()
        logging.info(f'Editted lesson_card object after editting a lesson ({instance.lesson_title}).')


@receiver(post_save, sender=lesson_completed_record)
def when_lesson_completed_notification_sent_by_teacher(sender, instance:lesson_completed_record, created, **kwargs):
    '''
    代表建立了新資料，此時必須要回去將對應的課程預約狀態 booked_status 改成等待學生確認中
    '''
    if created:
        # 只有建立新資料才要進行這個動作
        lesson_booking_object = lesson_booking_info.objects.get(id = instance.lesson_booking_info_id)

        lesson_booking_object.booking_status = 'student_not_yet_confirmed'
        lesson_booking_object.last_changed_by = 'teacher'  # 因為 因老師而改變此則預約的狀態
        lesson_booking_object.save()

        # email通知學生要進行完課時數確認
        #from .email_sending import lesson_email_manager
        #send_email = lesson_email_manager()
        #send_email.send_student_confirm_time_when_teacher_completed_lesson(
        #    student_authID = instance.student_auth_id)
        # 提醒老師要評價學生
        #send_email.send_teacher_rate_student_when_teacher_completed_lesson(
        #    teacher_authID = instance.teacher_auth_id)


            
@receiver(pre_save, sender=lesson_booking_info)
def update_receiving_review_lesson_minutes(sender, instance:lesson_booking_info, **kwargs):
    '''
    這裡要做的是，當狀態從 non-finished 變成 finished 時，要更新學生與老師的總上課時數；
    但因為需要學生進行確認，所以 不可能有一開始就是 finished 的狀況
    '''
    
    if instance.id is None:
        pass  # 只有改動的時候才需要注意
    else:
        previous = lesson_booking_info.objects.get(id=instance.id)
        if previous.booking_status != 'finished' and instance.booking_status == 'finished' :
            from account.models import student_review_aggregated_info
            from account.models import teacher_review_aggregated_info
            # 代表經過這次更改後才變成完課狀態，此時可以將課程的時數更新至學生的評價紀錄裏了
            
            the_student_review_info_object = \
                student_review_aggregated_info.objects.filter(student_auth_id=instance.student_auth_id).first()

            the_teacher_review_info_object = \
                teacher_review_aggregated_info.objects.filter(teacher_auth_id=instance.teacher_auth_id).first()

            lesson_completed_object = \
                lesson_completed_record.objects.get(lesson_booking_info_id=instance.id)
            
            # 先做學生的部份
            if the_student_review_info_object is None:
                # 代表沒有這筆記錄，可能是學生在QUIKOK PILOT時就已經註冊，才會沒有連動建立資料
                # 所以我們幫他建立一下吧
                student_review_aggregated_info.objects.create(
                    student_auth_id = instance.student_auth_id,
                    receiving_review_lesson_minutes_sum = \
                        lesson_completed_object.teacher_declared_time_in_minutes, 
                )
            else:
                # 已經有這筆資料了，更新就好
                the_student_review_info_object.receiving_review_lesson_minutes_sum += \
                    lesson_completed_object.teacher_declared_time_in_minutes
                the_student_review_info_object.save()

            # 開始更新老師的部份
            if the_teacher_review_info_object is None:
                # 代表沒有這筆記錄，可能是老師在QUIKOK PILOT時就已經註冊，才會沒有連動建立資料
                # 所以我們幫他建立一下吧
                teacher_review_aggregated_info.objects.create(
                    teacher_auth_id = instance.teacher_auth_id,
                    receiving_review_lesson_minutes_sum = \
                        lesson_completed_object.teacher_declared_time_in_minutes, 
                )
            else:
                # 已經有這筆資料了，更新就好
                the_teacher_review_info_object.receiving_review_lesson_minutes_sum += \
                    lesson_completed_object.teacher_declared_time_in_minutes
                the_teacher_review_info_object.save()



@receiver(post_save, sender=student_reviews_from_teachers)
def update_student_review_aggregated_info(sender, instance:student_reviews_from_teachers, created, **kwargs):
    '''
    當有老師給予學生評價(創建新紀錄)時，必須要連帶的更新該學生的評價儀表板，
    這邊要確認課程是否有完結(finished)，因為學生/老師會留存上過多長課程的資料，
    若還沒有雙方確認的時數的話，則不進行上課總時數的更新。
    '''
    from account.models import student_review_aggregated_info

    if created:
        # 只有建立新資料才要進行這個動作，其實編輯也需要啦，但是先不管這件事
        the_student_review_info_object = \
            student_review_aggregated_info.objects.filter(student_auth_id=instance.student_auth_id).first()
        
        if the_student_review_info_object is None:
            # 代表沒有這筆記錄，可能是學生在QUIKOK PILOT時就已經註冊，才會沒有連動建立資料
            # 所以我們幫他建立一下吧
            student_review_aggregated_info.objects.create(
                student_auth_id = instance.student_auth_id,
                score_given_sum = 0 if instance.score_given is None else instance.score_given,
                reviewed_times = 1,
                receiving_review_lesson_minutes_sum = 0,  # 這個值不在這邊進行更新
                is_student_late_for_lesson_times = 1 if instance.is_student_late_for_lesson == True else 0,
                is_student_frivolous_in_lesson_times = 1 if instance.is_student_frivolous_in_lesson == True else 0,
                is_student_or_parents_not_friendly_times = 1 if instance.is_student_or_parents_not_friendly == True else 0
            )
        else:
            # 代表已經有這筆紀錄，我們只要協助更新即可
            the_student_review_info_object.score_given_sum += \
                0 if instance.score_given is None else instance.score_given
            the_student_review_info_object.reviewed_times += 1
            # receiving_review_lesson_minutes_sum 不在這邊進行更新
            the_student_review_info_object.is_student_late_for_lesson_times += \
                1 if instance.is_student_late_for_lesson == True else 0
            the_student_review_info_object.is_student_frivolous_in_lesson_times += \
                1 if instance.is_student_frivolous_in_lesson == True else 0
            the_student_review_info_object.is_student_or_parents_not_friendly_times += \
                1 if instance.is_student_or_parents_not_friendly == True else 0
            the_student_review_info_object.save()

    else:
        # 代表學生的評價被更新，雖然目前沒有這個機制，但有可能是 Quikok 後台改動的
        # 因此這邊其實也需要做學生的評價更新，但我們先不管它
        pass


@receiver(post_save, sender=lesson_reviews_from_students)
def update_teacher_review_aggregated_info(sender, instance:lesson_reviews_from_students, created, **kwargs):
    '''
    當有學生給予老師評價(創建新紀錄)時，必須要連帶的更新該老師的評價儀表板，
    這邊要確認課程是否有完結(finished)，因為學生/老師會留存上過多長課程的資料，
    若還沒有雙方確認的時數的話，則不進行上課總時數的更新。
    '''
    from account.models import teacher_review_aggregated_info

    if created:
        # 只有建立新資料才要進行這個動作，其實編輯也需要啦，但是先不管這件事
        the_teacher_review_info_object = \
            teacher_review_aggregated_info.objects.filter(teacher_auth_id=instance.teacher_auth_id).first()
        
        if the_teacher_review_info_object is None:
            # 代表沒有這筆記錄，可能是學生在QUIKOK PILOT時就已經註冊，才會沒有連動建立資料
            # 所以我們幫他建立一下吧
            teacher_review_aggregated_info.objects.create(
                teacher_auth_id = instance.teacher_auth_id,
                score_given_sum = 0 if instance.score_given is None else instance.score_given,
                reviewed_times = 1,
                receiving_review_lesson_minutes_sum = 0,  # 這個值不在這邊進行更新
                is_teacher_late_for_lesson_times = 1 if instance.is_teacher_late_for_lesson == True else 0,
                is_teacher_frivolous_in_lesson_times = 1 if instance.is_teacher_frivolous_in_lesson == True else 0,
                is_teacher_incapable_times = 1 if instance.is_teacher_incapable == True else 0
            )
        else:
            # 代表已經有這筆紀錄，我們只要協助更新即可
            the_teacher_review_info_object.score_given_sum += \
                0 if instance.score_given is None else instance.score_given
            the_teacher_review_info_object.reviewed_times += 1
            # receiving_review_lesson_minutes_sum 不在這邊進行更新
            the_teacher_review_info_object.is_teacher_late_for_lesson_times += \
                1 if instance.is_teacher_late_for_lesson == True else 0
            the_teacher_review_info_object.is_teacher_frivolous_in_lesson_times += \
                1 if instance.is_teacher_frivolous_in_lesson == True else 0
            the_teacher_review_info_object.is_teacher_incapable_times += \
                1 if instance.is_teacher_incapable == True else 0
            the_teacher_review_info_object.save()

    else:
        # 代表老師的評價被更新，雖然目前沒有這個機制，但有可能是 Quikok 後台改動的
        # 因此這邊其實也需要做老師的評價更新，但我們先不管它
        pass


@receiver(pre_save, sender=lesson_info)
def when_lesson_info_changed_before_saving(sender, instance:lesson_info, **kwargs):
    '''
    當 lesson_info 這個 table 有新建課程或是編輯課程的動作時，要同步對 lesson_sales_sets 進行更新。    
    '''

    # = = = = = = = = 這裡用來執行 萃取課程特徵/屬性 = = = = = = = = 
    instance.hidden_lesson_attributes = \
        extract_subject_attributes_from_lesson(
            big_title=instance.big_title,
            little_title=instance.little_title,
            lesson_title=instance.lesson_title,
            highlight_1=instance.highlight_1,
            highlight_2=instance.highlight_2,
            highlight_3=instance.highlight_3,
            lesson_intro=instance.lesson_intro,
            how_does_lesson_go=instance.how_does_lesson_go,
            lesson_remarks=instance.lesson_remarks,
            lesson_attributes = instance.lesson_attributes
        )
    # = = = = = = = = 這裡用來執行 萃取課程特徵/屬性 = = = = = = = = 
    #if instance.selling_status == 'selling':
        # 先確定該門課程的狀態是販售中再做就好
    if instance.id is None:
        # 代表這個課程是全新建立的，因此不用比對舊資料，
        # 也不需要新增方案，因為課程第一次建立時並沒有對應的id（pre_save），
        # 並且目前的課程建立機制是兩段式，會先 create 一個幾乎完成的dummy record，
        # 再補上正確的課程資料夾路徑後，才算是正式完成。
        pass
        
    else:
        # 課程進行編輯，這時候要先將舊的方案都 disabled 掉，再更新新的上去就好。
        # 不過更新前先確定新舊是否一致，如果完全一致的話就不動，只要其中一個不一致就全動，
        # 避免老師只是更改課程的其他內容而已。
        previous = lesson_info.objects.get(id=instance.id)

        from_selling_to_not_selling = \
            previous.selling_status == 'selling' and instance.selling_status != 'selling'
        from_selling_to_selling = \
            previous.selling_status == 'selling' and instance.selling_status == 'selling'
        from_not_selling_to_selling = \
            previous.selling_status != 'selling' and instance.selling_status == 'selling'
        from_not_selling_to_not_selling = \
            previous.selling_status != 'selling' and instance.selling_status != 'selling'
    
        if from_not_selling_to_not_selling:
            # 什麼事情都不用做
            pass
        elif from_selling_to_not_selling:
            # 只要將所有的 is_open 方案變成 non-open 就好
            old_sales_sets = \
                lesson_sales_sets.objects.filter(lesson_id=instance.id, is_open=True)
            old_sales_sets.update(is_open=False)
            logging.info(f"Old lesson sales sets have been all disabled due to non-selling.")
        else:
            shared_columns = {
                'lesson_id': instance.id,
                'teacher_auth_id': instance.teacher.auth_id,
                'price_per_hour': instance.price_per_hour,
                'is_open': True}

            if from_not_selling_to_selling:
                # 全部都要新增，並且不用管舊的資料
                if int(instance.trial_class_price) != -999:
                    # 有試課方案
                    shared_columns['sales_set'] = 'trial'
                    shared_columns['total_hours_of_the_sales_set'] = 1
                    shared_columns['price_per_hour_after_discount'] = instance.trial_class_price
                    shared_columns['total_amount_of_the_sales_set'] = instance.trial_class_price
                    # 試課時間是30分鐘,因此除以3,取小數點後第5位
                    shared_columns['price_per_10_minutes'] = handy_round(int(instance.trial_class_price/3), 5) 
                    lesson_sales_sets.objects.create(
                        **shared_columns
                    ).save()
                                    
                if instance.lesson_has_one_hour_package == True:
                    # 有單堂方案
                    shared_columns['sales_set'] = 'no_discount'
                    shared_columns['total_hours_of_the_sales_set'] = 1
                    shared_columns['price_per_hour_after_discount'] = instance.price_per_hour
                    shared_columns['total_amount_of_the_sales_set'] = instance.price_per_hour
                    # 單堂課時間是60分鐘,因此除以6,取小數點後第5位
                    shared_columns['price_per_10_minutes'] = handy_round(int(instance.price_per_hour) /6 ,5)

                    lesson_sales_sets.objects.create(
                        **shared_columns
                    ).save()

                if len(instance.discount_price) > 2:
                    # 有其他方案
                    for each_hours_discount_set in [_ for _ in instance.discount_price.split(';') if len(_) > 0]:
                        
                        hours, discount_price = each_hours_discount_set.split(':')
                        shared_columns['sales_set'] = each_hours_discount_set
                        shared_columns['total_hours_of_the_sales_set'] = int(hours)
                        shared_columns['price_per_hour_after_discount'] = round(int(instance.price_per_hour)* int(discount_price) / 100)
                        shared_columns['total_amount_of_the_sales_set'] = round(int(instance.price_per_hour)* int(hours)* int(discount_price)/ 100)
                        # 單堂課時間是60分鐘,因此除以6,取到小數點後第5位
                        shared_columns['price_per_10_minutes'] = handy_round(int(instance.price_per_hour) * int(discount_price) / 100 / 6, 5) 

                        lesson_sales_sets.objects.create(
                            **shared_columns
                        ).save()

            elif from_selling_to_selling:
                # 先檢查跟舊的課程方案一不一樣，不一樣的話就 disabled 後新增
                if lesson_sales_sets.objects.filter(lesson_id=instance.id).exists() == False:
                    # 代表這是課程建立的那一次「編輯」
                    sales_sets_not_changed = False
                else:
                    sales_sets_not_changed = \
                        (
                            int(instance.trial_class_price) == int(previous.trial_class_price) and
                            instance.lesson_has_one_hour_package == previous.lesson_has_one_hour_package and
                            instance.discount_price == previous.discount_price and
                            int(instance.price_per_hour) == int(previous.price_per_hour)
                        )  # 確認是否完全一致
                
                if sales_sets_not_changed == False:
                    # 先把舊的方案都 disabled 掉
                    old_sales_sets = \
                        lesson_sales_sets.objects.filter(lesson_id=instance.id, is_open=True)
                    old_sales_sets.update(is_open=False)

                    logging.info(f"Old lesson sales sets have been disabled due to unmatched.")

                    # 要先確定 1.是否有試課方案  2.是否有單堂方案  3.其他方案(\d*:\d*的格式)
                    if int(instance.trial_class_price) != -999:
                        # 有試課方案
                        shared_columns['sales_set'] = 'trial'
                        shared_columns['total_hours_of_the_sales_set'] = 1
                        shared_columns['price_per_hour_after_discount'] = instance.trial_class_price
                        shared_columns['total_amount_of_the_sales_set'] = instance.trial_class_price
                        shared_columns['price_per_10_minutes'] = handy_round(int(instance.trial_class_price) / 3, 5)
                        # 試課時間是30分鐘,因此除以3,取小數點後第5位
                        
                        lesson_sales_sets.objects.create(
                            **shared_columns
                        ).save()
                        logging.info(f"Trial sets have been established.")
                    
                    if instance.lesson_has_one_hour_package == True:
                        # 有單堂方案
                        shared_columns['sales_set'] = 'no_discount'
                        shared_columns['total_hours_of_the_sales_set'] = 1
                        shared_columns['price_per_hour_after_discount'] = instance.price_per_hour
                        shared_columns['total_amount_of_the_sales_set'] = instance.price_per_hour
                        # 單堂課時間是60分鐘,因此除以6,取小數點後第5位
                        shared_columns['price_per_10_minutes'] = handy_round(int(instance.price_per_hour) / 6,5)
                        lesson_sales_sets.objects.create(
                            **shared_columns
                        ).save()

                        logging.info(f"No_discount sets have been established.")

                    if len(instance.discount_price) > 2:
                        # 有其他方案
                        logging.info(f"instance.discount_price: {instance.discount_price}")
                        for each_hours_discount_set in [_ for _ in instance.discount_price.split(';') if len(_) > 0]:
                            
                            hours, discount_price = each_hours_discount_set.split(':')
                            shared_columns['sales_set'] = each_hours_discount_set
                            shared_columns['total_hours_of_the_sales_set'] = int(hours)
                            shared_columns['price_per_hour_after_discount'] = handy_round(int(instance.price_per_hour) * int(discount_price) / 100, 0)
                            shared_columns['total_amount_of_the_sales_set'] = handy_round(int(instance.price_per_hour) * int(hours) * int(discount_price)/ 100, 0)
                            # 單堂課時間是60分鐘,因此除以6,取到小數點後第5位
                            shared_columns['price_per_10_minutes'] = handy_round(int(instance.price_per_hour) * int(discount_price) / 100 / 6, 5) 

                            lesson_sales_sets.objects.create(
                                **shared_columns
                            )
                            logging.info(f"sales set created: {shared_columns}")
                            
                        logging.info(f"Discount sets have been established.")
                else:
                    # sales sets have not been changed
                    pass

        logging.info(f"Lesson sales sets have been updated after lesson editted ({instance.lesson_title}).")



    