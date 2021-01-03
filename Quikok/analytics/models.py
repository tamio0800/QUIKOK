from django.db import models
# from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from analytics.signals import object_accessed_signal

# User = settings.AUTH_USER_MODEL

class object_accessed_info(models.Model):
    auth_id = models.PositiveIntegerField(blank=True, null=True)  # nullable，這樣即使user沒登入也看得到
    ip_address = models.CharField(max_length=220, blank=True, null=True)   # there is an IP Field
    url_path = models.CharField(max_length=100, blank=True, null=True)  # user 在哪一個頁面瀏覽
    api_name = models.CharField(max_length=100, blank=True, null=True)  # user 使用哪個 api
    model_name = models.CharField(max_length=55, blank=True, null=True)  # App 裡面的 models
    object_name = models.CharField(max_length=55, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)  #  models 下面的細項
    action_type = models.CharField(max_length=50, blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.object_name} viewed by {self.ip_address} on {str(self.timestamp).split(".")[0]}'

    class Meta:
        ordering= ['-timestamp']  # 越新的會被呈現在越上面
        verbose_name = 'Object Viewed'
        verbose_name_plural = 'Objects Viewed'

@receiver(object_accessed_signal)
def update_object_accessed_info(sender, **kwargs):
    '''
    將前端傳送的資料儲存到 object_accessed_info ，以備日後分析使用。
    這裡會扣掉來自本機端 127.0.0.1 的資訊，但測試中先不扣掉
    '''
    #print(f'update_object_accessed_info\n{sender}  {kwargs.items()}')
    # dict_items([('signal', <django.dispatch.dispatcher.Signal object at 0x7ff567bb3a90>), 
    # ('auth_id', None), ('ip_address', '127.0.0.1'), ('url_path', '/articles/article=4/'), 
    # ('model_name', 'article_info'), ('object_id', '4'), ('action_type', 'reading'), ('remark', None)])
    object_accessed_info.objects.create(
        auth_id=kwargs.get('auth_id'),
        ip_address=kwargs.get('ip_address'),
        url_path=kwargs.get('url_path'),
        api_name=sender,
        model_name=kwargs.get('model_name'),
        object_name=kwargs.get('object_name'),
        object_id=kwargs.get('object_id'),
        action_type=kwargs.get('action_type'),
        remark=kwargs.get('remark')
    ).save()
