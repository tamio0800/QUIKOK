from django.test import TestCase
from .models import exam_bank_sales_set

# 設定環境變數 DEV_MODE 為true >>  export DEV_MODE=true
# 取消環境變數 DEV_MODE >> unset DEV_MODE
# python3 manage.py test amigo/ --settings=Quikok.settings_for_test

class test_exam_bank(TestCase):
    def test_create_exam_bank_sales_set(self):
        exam_bank_sales_set.objects.create(
            duration ='365days', # 販售的時間單位,暫時還未定預想會換算成day
            selling_price = 500
        )
        self.assertEqual(exam_bank_sales_set.objects.all().count(),1)