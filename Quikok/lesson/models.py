from django.db import models
from account.models import teacher_profile, student_profile
from datetime import timedelta, date as date_function
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

class lesson_info(models.Model): # 0903架構還沒想完整先把確定有的東西填入
    # 每堂課程會有自己的unique id，我們用這個來辨識、串連課程 09/25 討論後認為先用內建的id就好
    # lesson_id = models.CharField(max_length = 40) 
    teacher = models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='teacher_of_the_lesson')
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
    trial_class_price = models.IntegerField()  # 該門課程的試上鐘點費, 若無試教則為 -999
    discount_price = models.CharField(max_length = 30) # 優惠折數
    # discount_price說明
    # 假設老師勾選了方案一 & 方案二 & 方案三，內容各自為：
    # 一次購買「10」小時，提供總價「95」%優惠價..
    # 一次購買「20」小時，提供總價「80」%優惠價..
    # 一次購買「30」小時，提供總價「70」%優惠價..
    # 此時 discount_price >> "10:95;20:80;30:70;"。
    # 若只勾選方案一，則為：
    # discount_price >> "10:95;"
    highlight_1 = models.CharField(max_length = 10)  # 亮點介紹1，不要超過10個字元長
    highlight_2 = models.CharField(max_length = 10)  # 亮點介紹2，不要超過10個字元長
    highlight_3 = models.CharField(max_length = 10)  # 亮點介紹3，不要超過10個字元長
    lesson_intro = models.TextField(blank=True, null=True)
    # lesson_intro = models.CharField(blank=True, max_length=300)
    # 課程詳細介紹，不超過300長度
    how_does_lesson_go = models.TextField(blank=True, null=True)
    # how_does_lesson_go = models.CharField(blank=True, max_length=200)
    # 課程方式/教學方式，舉例來說：「本堂課前十分鐘小考，測驗上次的內容吸收程度，
    # 接著正式上課兩小時，最後15分鐘溫習。」
    target_students = models.TextField(blank=True, null=True) # 授課對象
    lesson_remarks = models.TextField(blank=True, null=True) # 備註，目前是用來儲存「給學生的注意事項」
    # lesson_background_folder = models.CharField(max_length = 80)# 該課程背景圖片指向的資料夾 可選預設或上傳
    # lesson_picture_folder = models.CharField(max_length = 80) # 目前版本用不到本col 如果目前版本用不到本col有相關圖片，可以儲存在這個資料夾中
    syllabus = models.TextField(blank=True, null=True) 
    # 存放課程的綱要或架構，預計會以html的方式傳遞/儲存 格式:大標/小標:內容; 
    # lesson_appendix_folder = models.CharField(max_length = 80)
    # 目前版本用不到本col 如果將來有相關附件，可以儲存在這個資料夾中
    # 這裡還要記得把老師的有空時段連過來
    # is_approved = models.BooleanField(default=False)
    lesson_attributes = models.TextField(blank = True)  
    # 這個是放課程的標籤，一開始先人工(老師)給，之後再交給機器學習模型來判斷
    lesson_avg_score = models.FloatField(default = 0.0) # 這個是平均評分，每次評分表一更新這裡也會連動更新
    lesson_reviewed_times = models.IntegerField(default = 0) # 這個是課程被評分過幾次的統計
    created_time = models.DateTimeField(auto_now_add=True)
    edited_time = models.DateTimeField(auto_now=True)
    selling_status = models.CharField(max_length = 20)
    # 販售狀態 >>
    #   草稿: draft, 上架: selling, 沒上架: notSelling, 刪除: donotShow
    def __str__(self):
        return self.lesson_title

    class Meta:
        verbose_name = '課程詳細資訊'
        verbose_name_plural = '課程詳細資訊'


class lesson_card(models.Model):
    # 這個table用來儲存課程小卡的資訊，原因是當我們課程變多的時候，
    # 要即時組合老師、課程、評價資訊會需要大量的運算，不如多建立一個table，
    # 之後直接query就好。
    corresponding_lesson_id = models.IntegerField()  # 所對應的課程id
    teacher_thumbnail_path = models.TextField(blank=True)  # 老師的大頭照路徑
    teacher_nickname = models.CharField(max_length = 40)
    teacher_auth_id = models.IntegerField()
    is_this_teacher_male = models.BooleanField(default=True)
    big_title = models.CharField(max_length = 10)  # 背景圖片的大標題
    little_title = models.CharField(max_length = 10)  # 背景圖片的小標題
    title_color = models.CharField(max_length = 7)    
    background_picture_code = models.IntegerField()
    background_picture_path = models.TextField(blank=True) # 指向上傳圖的路徑
    lesson_title = models.CharField(max_length = 14) # 課程的名稱
    highlight_1 = models.CharField(max_length = 10)  # 亮點介紹1，不要超過10個字元長
    highlight_2 = models.CharField(max_length = 10)  # 亮點介紹2，不要超過10個字元長
    highlight_3 = models.CharField(max_length = 10)  # 亮點介紹3，不要超過10個字元長
    price_per_hour = models.IntegerField()  # 該門課程的鐘點費
    best_sale = models.CharField(max_length = 20) # 用來吸引人的最優惠折價標語
    education = models.CharField(max_length = 60, blank=True)  # 最高學歷說明
    education_is_approved = models.BooleanField()
    working_experience = models.CharField(max_length = 100, blank=True)  # 經歷說明
    working_experience_is_approved = models.BooleanField()
    lesson_avg_score = models.FloatField(default = 0.0) # 這個是平均評分，每次評分表一更新這裡也會連動更新
    lesson_reviewed_times = models.IntegerField(default = 0) # 這個是課程被評分過幾次的統計
  
    def __str__(self):
        return self.lesson_title

    class Meta:
        verbose_name = '課程小卡資訊'
        verbose_name_plural = '課程小卡資訊'


'''class lesson_info_snapshot(models.Model): 
    # 加上課程更改的snapshot，其中價格的變更一定要留存
    # 主要為了證明對方真的有更改過那個價格，而且也為了之後資料分析怎麼樣的設計有助於吸引顧客。
    lesson_id = models.CharField(max_length=20) 
    teacher = models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='teacher_of_the_lesson_snapshot')
    lesson_title = models.CharField(max_length = 10) # 課程的名稱
    price_per_hour = models.IntegerField()  # 該門課程的費用(時薪)
    highlight_1 = models.CharField(max_length = 10)  # 亮點介紹1，不要超過10個字元長
    highlight_2 = models.CharField(max_length = 10)  # 亮點介紹2，不要超過10個字元長
    highlight_3 = models.CharField(max_length = 10)  # 亮點介紹3，不要超過10個字元長
    lesson_intro = models.CharField(blank=True, max_length = 300)
    # 課程詳細介紹，不超過300長度
    how_does_lesson_go = models.CharField(blank=True, max_length=200)
    # 課程方式/教學方式，舉例來說：「本堂課前十分鐘小考，測驗上次的內容吸收程度，
    # 接著正式上課兩小時，最後15分鐘溫習。」
    lesson_remark = models.CharField(blank=True, max_length=200)
    # lesson_picture_folder = models.CharField(max_length=60)
    # 課程snapshot應該不需要這個吧？  >>   如果課程有相關圖片，可以儲存在這個資料夾中
    syllabus = models.CharField(max_length=400)
    # 這個用來存放課程的綱要或架構，預計會以陣列的方式傳遞/儲存
    # lesson_appendix_folder = models.CharField(max_length=60)
    # 課程snapshot應該不需要這個吧？  >>   如果課程有相關附件，可以儲存在這個資料夾中
    lesson_attributes = models.CharField(blank=True, max_length=50)
    first_created_time = models.DateTimeField()
    last_modified_time = models.DateTimeField(auto_created=True)
    # 這裡還要記得把老師的有空時段連過來

    def __str__(self):
        return self.lesson_id'''
        

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
        return str(self.id)

    class Meta:
        verbose_name = '學生對老師/課程評價'
        verbose_name_plural = '學生對老師/課程評價'


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
        return str(self.id)

    class Meta:
        verbose_name = '老師對學生評價'
        verbose_name_plural = '老師對學生評價'


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
    booking_start_datetime = models.DateTimeField(auto_now=True)
    # Example: 2020-08-21:1,2,3,4; 之類的
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
        return f"學生({str(self.student_auth_id)})預約老師({str(self.teacher_auth_id)})的課程({str(self.lesson_id)})的方案({str(self.booking_set_id)})。 目前狀態:{self.booking_status}; 最後更改時間:{self.last_changed_time.strftime('%Y-%m-%d %H:%M:%S')}"

    def get_booking_date(self):
        # 回傳這次的預約日期
        return date_function([int(_) for _ in self.booking_date_and_time.split(':')[0].split('-')])

    def get_booking_time_in_minutes(self):
        # 回傳這次的預約總計多少分鐘
        return int(len(self.booking_date_and_time[:-1].split(':')[1].split(','))) * 30

    class Meta:
        verbose_name = '課程預約資訊'
        verbose_name_plural = '課程預約資訊'


# 上課與完課紀錄
class lesson_completed_record(models.Model):
    lesson_booking_info_id = models.IntegerField()  # 對應的課程id
    student_remaining_minutes_of_each_purchased_lesson_set_id= models.IntegerField()
    # 對應的訂單所剩的時數
    teacher_auth_id = models.IntegerField()
    student_auth_id = models.IntegerField()
    booking_time_in_minutes = models.IntegerField() # 預估上課時間時數,單位分鐘,是用預約的時間計算的
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
    created_time = models.DateTimeField(auto_now_add=True)
    last_changed_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = '完課紀錄'
        verbose_name_plural = '完課紀錄'
        

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
        return str(self.id)
    
    class Meta:
        verbose_name = '課程方案資訊'
        verbose_name_plural = '課程方案資訊'


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



@receiver(post_save, sender=lesson_completed_record)
def when_lesson_completed_notification_sent_by_teacher(sender, instance:lesson_completed_record, created, **kwargs):
    # 代表建立了新資料，此時必須要回去將對應的課程預約狀態 booked_status 改成等待學生確認中
    if created:
        # 只有建立新資料才要進行這個動作
        lesson_booking_object = lesson_booking_info.objects.get(id = instance.lesson_booking_info_id)

        lesson_booking_object.booking_status = 'student_not_yet_confirmed'
        lesson_booking_object.last_changed_by = 'teacher'  # 因為 因老師而改變此則預約的狀態
        lesson_booking_object.save()

        # 通知學生要進行完課時數確認
        from .email_sending import email_manager
        send_email = email_manager()
        send_email.send_student_confirm_time_when_teacher_completed_lesson(
            student_authID = instance.student_auth_id)
        # 提醒老師要評價學生
        send_email.send_teacher_rate_student_when_teacher_completed_lesson(
            teacher_authID = instance.teacher_auth_id)
            
@receiver(pre_save, sender=lesson_booking_info)
def update_receiving_review_lesson_minutes(sender, instance:lesson_booking_info, **kwargs):
    # 這裡要做的是，當狀態從 non-finished 變成 finished 時，要更新學生與老師的總上課時數
    # 但因為需要學生進行確認，所以 不可能有一開始就是 finished 的狀況
    
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
    # 當有老師給予學生評價(創建新紀錄)時，必須要連帶的更新該學生的評價儀表板
    from account.models import student_review_aggregated_info
    # 這邊要確認課程是否有完結(finished)，因為學生/老師會留存上過多長課程的資料，
    # 若還沒有雙方確認的時數的話，則不進行上課總時數的更新；
    # 這代表未來要再寫一個機制，當課程狀態從非 finished 變成 finished 時，要更新 student_review_aggregated_info 的上課時數
    # >> 我決定先不在這邊進行時數更新，免得有兩邊都更新到的疑慮存在，這個欄位統一在 非 finished 變成 finished 更新!
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
    # 當有學生給予老師評價(創建新紀錄)時，必須要連帶的更新該老師的評價儀表板
    from account.models import teacher_review_aggregated_info
    # 這邊要確認課程是否有完結(finished)，因為學生/老師會留存上過多長課程的資料，
    # 若還沒有雙方確認的時數的話，則不進行上課總時數的更新；
    # 這代表未來要再寫一個機制，當課程狀態從非 finished 變成 finished 時，要更新 student_review_aggregated_info 的上課時數
    # >> 我決定先不在這邊進行時數更新，免得有兩邊都更新到的疑慮存在，這個欄位統一在 非 finished 變成 finished 更新!
    if created:
        # 只有建立新資料才要進行這個動作，其實編輯也需要啦，但是先不管這件事
        the_teacher_review_info_object = \
            teacher_review_aggregated_info.objects.filter(teacher_auth_id=instance.teacher_auth_id).first()
        
        if the_teacher_review_info_object is None:
            # 代表沒有這筆記錄，可能是學生在QUIKOK PILOT時就已經註冊，才會沒有連動建立資料
            # 所以我們幫他建立一下吧
            the_teacher_review_info_object.objects.create(
                teacher_auth_id = instance.teacher_auth_id,
                score_given_sum = 0 if instance.score_given is None else instance.score_given,
                reviewed_times = 1,
                receiving_review_lesson_minutes_sum = 0,  # 這個值不在這邊進行更新
                is_teacher_late_for_lesson = 1 if instance.is_teacher_late_for_lesson == True else 0,
                is_teacher_frivolous_in_lesson = 1 if instance.is_teacher_frivolous_in_lesson == True else 0,
                is_teacher_incapable = 1 if instance.is_teacher_incapable == True else 0
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



    