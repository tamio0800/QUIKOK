# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from account.models import student_profile, teacher_profile


class chat_room(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE,related_name='student_set')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,related_name='teacher_set')
    date= models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return 'member:{},{}'.format(self.student,self.teacher)


class Messages(models.Model):
    """
    Model to represent user submitted changed to a resource guide
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    group = models.ForeignKey(chat_room, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String to represent the message
        """
        return self.message

#class user_info_chat(models.Model):
#    member1= models.ForeignKey(User, on_delete=models.CASCADE,related_name='member1')
 #   member2= models.ForeignKey(User, on_delete=models.CASCADE,related_name='member2')
 #   member1_snapshot = models.TextField(null = True)
 #   member2_snapshot = models.TextField(null = True)

 #   def __str__(self):
 #       return self.user_info_chat

# !!!!!!!!!!!!!!  新增models於下 by tata  !!!!!!!!!!!!!!

class chatroom_info_user2user(models.Model):
    '''
    用來紀錄、管理「user對user聊天室，1對1」的table；
    不在這裏建立「是否有未讀訊息」的欄位是因為沒辦法看出應該通知哪一方前來查看，
    如果還要串連「對話歷史table」才能分辨的話，倒不如一開始就做在「對話歷史table」。
    '''
    teacher_auth_id = models.IntegerField()
    student_auth_id = models.IntegerField()
    parent_auth_id = models.IntegerField()
    chatroom_type = models.CharField(max_length=30)
    # teacher2student  or  teacher2parent
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)


class chatroom_info_system2user(models.Model):
    '''
    用來管理「我們(Quikok)對user聊天室的table」，
    如果user在這個聊天室中傳訊息給我們我們或許也可以透過類似客服的機制來給予回應，
    另外像是匯款、收付、預定等等也可以透過這個聊天室來通知user。
    '''
    user_auth_id = models.IntegerField()
    user_type = models.CharField(max_length=20)    # teacher  or  student  or parent
    system_user_auth_id = models.IntegerField()  # 為了一致性及未來的客服需求而生的
    chatroom_type = models.CharField(max_length=30)  # 為了一致性及未來的客服需求而生的
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)


class chat_history_user2user(models.Model):
    '''
    user之間的對話紀錄
    '''
    chatroom_info_user2user_id = models.IntegerField()
    teacher_auth_id = models.IntegerField()
    student_auth_id = models.IntegerField()
    parent_auth_id = models.IntegerField()
    message = models.TextField()
    message_type = models.CharField(max_length=30)
    who_is_sender = models.CharField(max_length=20)    # teacher  or  student  or parent
    is_read = models.BooleanField()
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)


class chat_history_system2user(models.Model):
    '''
    系統與user的對話紀錄
    '''
    chatroom_info_system2user_id = models.IntegerField()
    user_auth_id = models.IntegerField()
    system_user_auth_id = models.IntegerField()  # 為了一致性及未來的客服需求而生的
    message = models.TextField()
    message_type = models.CharField(max_length=30)
    who_is_sender = models.CharField(max_length=20)  # teacher  or  student  or parent or system_user
    is_read = models.BooleanField()
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)


class default_notifications_from_system(models.Model):
    '''
    系統傳給user們的預設訊息格式。
    '''
    for_which_chatroom = models.CharField(max_length=20)  # user2user or system2user
    notification_code = models.CharField(max_length=20)  # 每個default訊息的代碼
    notification_context = models.CharField(max_length=200)
    # 如： '提醒您，您{}課程的剩餘時數只剩{}分鐘，是否立即前往購買新一期的課程呢？  優惠連結>>{}'
    created_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.notification_code)

