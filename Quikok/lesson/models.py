from django.db import models
from account.models import teacher_profile, student_profile

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
        

class lesson_reviews(models.Model):
    corresponding_lesson_id = models.IntegerField()  # 所對應的課程id
    student_auth_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()
    score_given = models.IntegerField() # 評分介於1~5分
    remark_given = models.TextField(blank=True, null=True)
    picture_folder = models.TextField # 加上真的有上課的圖以資證明（學蝦皮
    created_time = models.DateTimeField(auto_now_add=True)
    edited_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)


class lesson_booking_info(models.Model):
    '''
    課程的預約管理table，這個model是用來管理「每一則booking」的狀態與profile
    '''
    lesson_id = models.IntegerField()  # 所對應的課程id
    teacher_auth_id = models.IntegerField()
    student_auth_id = models.IntegerField()
    parent_auth_id = models.IntegerField(default=-1)
    booked_by = models.CharField(max_length = 20)  # teacher or student or parent
    last_changed_by = models.CharField(max_length = 20)  # teacher or student or parent
    booking_set = models.IntegerField()
    # 預約使用的是該課程的哪一個方案（ID），這個之後會另外建立一個「每個課程的方案table」來做串連。
    remaining_minutes = models.IntegerField()
    booking_date_and_time = models.CharField(max_length=400)  
    # Example: 2020821:1,2,3,4;20200822:3,4,5,6 之類的
    booking_status = models.CharField(max_length = 20)  # to_be_confirmed or confirmed or canceled
    created_time = models.DateTimeField(auto_now_add=True)
    last_changed_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)


class lesson_complete_record(models.Model):
    lesson_booking_info_id = models.IntegerField()  # 所對應的課程id
    teacher_auth_id = models.IntegerField()
    student_auth_id = models.IntegerField()
    parent_auth_id = models.IntegerField(default=-1)
    real_teaching_time = models.IntegerField()
    # 實際開課時間
    real_start_time = models.DateTimeField(auto_now_add=True)
    # 實際下課時間
    real_end_time = models.DateTimeField(auto_now_add=True)
    # 實際上課時數, 1分鐘為單位, 10分鐘一跳
    check_time = models.IntegerField()
    # 實際應付老師金額
    real_teaching_fee = models.IntegerField()
    # # Example: 2020821:1,2,3,4;20200822:3,4,5,6 之類的
    teaching_status = models.CharField(max_length = 20)  
    # 還沒上課 unprocess, 已完課 over or canceled
    is_student_confirm = models.BooleanField(default=0)
    # default=0,當老師送出向學生確認後改為1, 萬一需要協調時數用
    created_time = models.DateTimeField(auto_now_add=True)
    last_changed_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
        

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
    is_open = models.BooleanField(default=True)  #是否為老師該課程目前使用中的方案
    def __str__(self):
        return str(self.id)

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

# 上課與完課紀錄
