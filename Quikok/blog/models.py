from django.db import models
from tinymce.models import HTMLField
import os, re

# Here are functions to deal with model contents.

def get_certain_length_article_content(html_strings, length, escape_tags_in_list):
    '''
    html_strings: 就是TinyMCE產生的html格式的文章
    length: 長度，中文長度為1，英文或是數字為0.5
    escape_tags_in_list: 這個函式會把除了放在這個變數中的html tags都去掉

    分辨英數字, 在ASCII編碼中，編號(含首尾):
        48-57:  0-9
        65-90:  A-Z
        97-122: a-z
        // 60:  <
        // 62:  >
    '''

    pattern = r'<.*?>'
    all_found_tags = [_ for _ in list(set(re.findall(pattern, html_strings))) if _ not in escape_tags_in_list]
    for each_tag in all_found_tags:
        html_strings = html_strings.replace(each_tag, '')

    html_strings = re.sub(r'&nbsp;', ' ', html_strings)
    
    
    temp_html_strings = ''
    length_count = 0
    for each_character in html_strings:
        circumstance = \
            ((48 <= ord(each_character) <= 57) or \
            (65 <= ord(each_character) <= 90) or \
            (97 <= ord(each_character) <= 122))
        # 先計算一下該character是不是英數字
        if circumstance:
            length_count += 0.5
        else:
            length_count += 1
        temp_html_strings += each_character

        if length_count > length:
            # 已經到達極限了
            return temp_html_strings + '...'

    # 沒有超過字數限制，直接回傳    
    return temp_html_strings
    

# Create your models here.
class article_info(models.Model):
    # 紀錄文章(部落格)的內容
    author_id = models.IntegerField()
    main_picture = \
        models.ImageField(
            default='articles/default_main_picture.png',
            upload_to='articles/%Y/%m/%d/')
    title = models.CharField(max_length=100)
    content = HTMLField()
    category = models.CharField(max_length=100)  # 文章的分類
    hashtag = models.TextField()
    created_time = models.DateTimeField(auto_now=True)
    last_edited_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.title)

    def snippet(self):
        return get_certain_length_article_content(self.content, 100, [])



class author_profile(models.Model):
    # 記錄作者資訊的內容
    auth_user_id = models.IntegerField(blank=True, null=True)  # 對應的auth_user_id, 可能為None值
    name = models.CharField(max_length=100)  # 筆名、真名、或暱稱都可以
    hightlight = models.CharField(max_length=20)  # 簡短的一行介紹
    intro = models.TextField()
    thumbnail = models.ImageField(
            default='authors/default_thumbnail.png',
            upload_to='authors/%Y/%m/%d/')  # 作者的大頭貼(一開始沒有沒關係)
    hashtag = models.TextField()  # 作者本身的hashtag
    created_time = models.DateTimeField(auto_now=True)
    last_edited_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.name)

