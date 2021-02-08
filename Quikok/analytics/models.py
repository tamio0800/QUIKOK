from django.db import models
# from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from analytics.signals import object_accessed_signal
from datetime import timedelta
from blog.models import article_info
import re

# User = settings.AUTH_USER_MODEL

class object_accessed_info(models.Model):
    auth_id = models.PositiveIntegerField(blank=True, null=True)  # nullable，這樣即使user沒登入也看得到
    ip_address = models.CharField(max_length=220, blank=True, null=True)   # there is an IP Field
    url_path = models.CharField(max_length=100, blank=True, null=True)  # user 在哪一個頁面瀏覽
    api_name = models.CharField(max_length=100, blank=True, null=True)  # user 使用哪個 api
    model_name = models.CharField(max_length=55, blank=True, null=True)  # App 裡面的 models
    object_name = models.CharField(max_length=55, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)  #  models 下面的細項
    user_agent = models.CharField(max_length=200, blank=True, null=True)
    action_type = models.CharField(max_length=50, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.object_name} viewed by {self.ip_address} on {str(self.timestamp + timedelta(hours=8)).split(".")[0]}'

    class Meta:
        ordering= ['-timestamp']  # 越新的會被呈現在越上面
        verbose_name = 'Object Viewed'
        verbose_name_plural = 'Objects Viewed'



@receiver(object_accessed_signal)
def update_object_accessed_info(sender, **kwargs):
    '''
    將前端傳送的資料儲存到 object_accessed_info ，以備日後分析使用。
    '''
    if kwargs.get('action_type') == 'auth_check':
        # 來自 auth_check 的訊號，需要特別處理
        # 先檢查 auth_id 是否為有效值
        if '/blog/post/' in kwargs.get('url_path'):
            # 是文章的url，轉成文章標題回傳
            matched_article_id = re.search(r'\d+', kwargs.get('url_path'))
            if matched_article_id is not None:
                matched_article_id = matched_article_id.group(0)
                object_accessed_info.objects.create(
                    auth_id=kwargs.get('auth_id'),
                    ip_address=kwargs.get('ip_address'),
                    url_path=kwargs.get('url_path'),
                    api_name='article_content',
                    model_name='aritcle_info',
                    object_name=article_info.objects.filter(id=matched_article_id).first().title,
                    object_id=matched_article_id,
                    user_agent=kwargs.get('user_agent'),
                    action_type=kwargs.get('action_type'),
                    remark=kwargs.get('remark')
                ).save()
        elif '/blog/main' in kwargs.get('url_path'):
            object_accessed_info.objects.create(
                auth_id=kwargs.get('auth_id'),
                ip_address=kwargs.get('ip_address'),
                url_path=kwargs.get('url_path'),
                api_name='main_blog',
                model_name='aritcle_info',
                object_name='main_blog',
                object_id=kwargs.get('object_id'),
                user_agent=kwargs.get('user_agent'),
                action_type=kwargs.get('action_type'),
                remark=kwargs.get('remark')
            ).save()
        elif 'landing' in kwargs.get('url_path'):
            object_accessed_info.objects.create(
                auth_id=kwargs.get('auth_id'),
                ip_address=kwargs.get('ip_address'),
                url_path=kwargs.get('url_path'),
                api_name=sender,
                model_name=kwargs.get('model_name'),
                object_name='landing_page',
                object_id=kwargs.get('object_id'),
                user_agent=kwargs.get('user_agent'),
                action_type=kwargs.get('action_type'),
                remark=kwargs.get('remark')
            ).save()
        elif '/account/register/teacher' in kwargs.get('url_path'):
            # 初次進到註冊老師的頁面
            object_accessed_info.objects.create(
                auth_id=kwargs.get('auth_id'),
                ip_address=kwargs.get('ip_address'),
                url_path=kwargs.get('url_path'),
                api_name=sender,
                model_name=kwargs.get('model_name'),
                object_name='teacher_register_page',
                object_id=kwargs.get('object_id'),
                user_agent=kwargs.get('user_agent'),
                action_type=kwargs.get('action_type'),
                remark=kwargs.get('remark')
            ).save()
        elif '/account/register/student' in kwargs.get('url_path'):
            # 初次進到註冊學生的頁面
            object_accessed_info.objects.create(
                auth_id=kwargs.get('auth_id'),
                ip_address=kwargs.get('ip_address'),
                url_path=kwargs.get('url_path'),
                api_name=sender,
                model_name=kwargs.get('model_name'),
                object_name='student_register_page',
                object_id=kwargs.get('object_id'),
                user_agent=kwargs.get('user_agent'),
                action_type=kwargs.get('action_type'),
                remark=kwargs.get('remark')
            ).save()
        elif '/lesson/guestready' in kwargs.get('url_path'):
            # 進到註冊前開課的頁面
            object_accessed_info.objects.create(
                auth_id=kwargs.get('auth_id'),
                ip_address=kwargs.get('ip_address'),
                url_path=kwargs.get('url_path'),
                api_name=sender,
                model_name='lesson_info_for_users_not_signed_up',
                object_name=kwargs.get('object_name'),
                object_id=kwargs.get('object_id'),
                user_agent=kwargs.get('user_agent'),
                action_type='create lesson before signup',
                remark=kwargs.get('remark')
            ).save()
        elif '/lesson/ready/add' in kwargs.get('url_path'):
            object_accessed_info.objects.create(
                auth_id=kwargs.get('auth_id'),
                ip_address=kwargs.get('ip_address'),
                url_path=kwargs.get('url_path'),
                api_name=sender,
                model_name='lesson_info',
                object_name=kwargs.get('object_name'),
                object_id=kwargs.get('object_id'),
                user_agent=kwargs.get('user_agent'),
                action_type='create lesson after signup',
                remark=kwargs.get('remark')
            ).save()
        
    else:
        object_accessed_info.objects.create(
                auth_id=kwargs.get('auth_id'),
                ip_address=kwargs.get('ip_address'),
                url_path=kwargs.get('url_path'),
                api_name=sender,
                model_name=kwargs.get('model_name'),
                object_name=kwargs.get('object_name'),
                object_id=kwargs.get('object_id'),
                user_agent=kwargs.get('user_agent'),
                action_type=kwargs.get('action_type'),
                remark=kwargs.get('remark')
            ).save()


            