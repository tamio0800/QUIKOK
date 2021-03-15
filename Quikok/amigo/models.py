from django.db import models

# 題庫販售組合，預想跟課程一樣會一直長下去

class exam_bank_sales_set(models.Model):
    duration = models.CharField(max_length=30, default='') 
    # 販售的時間單位,暫時還未定預想類似 1 month, 1 year ...
    selling_price = models.IntegerField() # 定價, 500 (元)
    created_time = models.DateTimeField(auto_now_add=True) 
    updated_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"題庫方案id: {str(self.id)}" 

    class Meta:
        verbose_name = '題庫販售方案'
        verbose_name_plural = '題庫販售方案'
        ordering = ['-updated_time']