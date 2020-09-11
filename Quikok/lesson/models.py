from django.db import models
from account.models import teacher_profile, student_profile


class lesson_info(models.Model): # 0903架構還沒想完整先把確定有的東西填入
    # 每堂課程會有自己的unique id，我們用這個來辨識、串連課程
    lesson_id = models.CharField(max_length=20) 
    teacher = models.ForeignKey(teacher_profile, on_delete=models.CASCADE, related_name='teacher_of_the_lesson')
    lesson_title = models.CharField(max_length = 10) # 課程的名稱
    price_per_hour = models.IntegerField()  # 該門課程的費用(時薪)
    highlight_1 = models.CharField(max_length = 10)  # 亮點介紹1，不要超過10個字元長
    highlight_2 = models.CharField(max_length = 10)  # 亮點介紹2，不要超過10個字元長
    highlight_3 = models.CharField(max_length = 10)  # 亮點介紹3，不要超過10個字元長
    lesson_intro = models.CharField(blank=True, max_length=300)
    # 課程詳細介紹，不超過300長度
    how_does_lesson_go = models.CharField(blank=True, max_length=200)
    # 課程方式/教學方式，舉例來說：「本堂課前十分鐘小考，測驗上次的內容吸收程度，
    # 接著正式上課兩小時，最後15分鐘溫習。」
    lesson_remarks = models.CharField(blank=True, max_length=200)
    lesson_picture_folder = models.CharField(max_length=60)
    # 如果課程有相關圖片，可以儲存在這個資料夾中
    syllabus = models.CharField(max_length=400)
    # 這個用來存放課程的綱要或架構，預計會以陣列的方式傳遞/儲存
    lesson_appendix_folder = models.CharField(max_length=60)
    # 如果課程有相關附件，可以儲存在這個資料夾中
    # 這裡還要記得把老師的有空時段連過來
    # is_approved = models.BooleanField(default=False)
    lesson_attributes = models.CharField(blank=True, max_length=50)  # 這個是放課程的屬性，一開始先人工(Quikok)給，之後再交給機器學習模型來判斷
    lesson_avg_score = models.FloatField(default=0.0) # 這個是平均評分，每次評分表一更新這裡也會連動更新
    lesson_reviewed_times = models.IntegerField(default=0) # 這個是課程被評分過幾次的統計
    created_time = models.DateTimeField(auto_created=True)
    
    def __str__(self):
        return self.lesson_id


class lesson_info_snapshot(models.Model): 
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
        return self.lesson_id


class lesson_reviews(models.Model):
    # 每堂課程會有自己的unique id，我們用這個來辨識、串連課程
    lesson_id = models.CharField(max_length=20)
    student = models.ForeignKey(student_profile, on_delete=models.CASCADE, related_name='student_of_the_lesson') # 誰留的評價
    score_given = models.IntegerField() # 評分介於1~5分
    remark_given = models.CharField(blank=True, max_length=50) # 可接受空白，不超過50字
    picture_folder = models.CharField(max_length=60) # 加上真的有上課的圖以資證明（學蝦皮） 

    def __str__(self):
        return self.lesson_id



