from django.test import TestCase
from django.test import Client
# Create your tests here.

class blog_articles_editor_test(TestCase):
    # 用來測試文章編輯器 & 預覽功能的測試class

    def setUp(self):
        self.client = Client()
    
    def test_editor_function_exitst(self):
        # 測試有這麼一個編輯器的url存在
        response = self.client.get('/articles/editor/')
        #print(response.content)
        '''
        因為我們在Quikok的url那邊設定如果是不存在的urls，
        一律都會導回首頁，導致理應出不來的連線也能回傳status_code==200，
        只好記得要用其他方式做測試。
        '''
        self.assertIn('文章編輯器', str(response.content, 'utf8'), str(response.content, 'utf8'))
