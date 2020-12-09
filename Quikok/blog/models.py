from django.db import models
from tinymce.models import HTMLField

# Create your models here.
class article_info(models.Model):
    # 紀錄文章(部落格)的內容
    author_id = models.IntegerField()
    title = models.CharField(max_length=100)
    content = HTMLField()
    category = models.CharField(max_length=100)  # 文章的分類
    hashtag = models.TextField()
    created_time = models.DateTimeField(auto_now=True)
    last_edited_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.title)

class author_profile(models.Model):
    # 記錄作者資訊的內容
    auth_user_id = models.IntegerField(blank=True, null=True)  # 對應的auth_user_id, 可能為None值
    name = models.CharField(max_length=100)  # 筆名、真名、或暱稱都可以
    hightlight = models.CharField(max_length=20)  # 簡短的一行介紹
    intro = models.TextField()
    thumbnail_path = models.TextField(blank=True, null=True)  # 作者的大頭貼路徑(一開始沒有沒關係)
    hashtag = models.TextField()  # 作者本身的hashtag
    created_time = models.DateTimeField(auto_now=True)
    last_edited_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.name)
