from django.test import TestCase, Client
from blog.models import article_info


# python manage.py test blog/ --settings=Quikok.settings_for_test

# Create your tests here.
class blog_articles_editor_test(TestCase):
    # 用來測試文章編輯器 & 預覽功能的測試class

    def setUp(self):
        self.client = Client()


    def test_editor_function_exist(self):
        # 測試有這麼一個編輯器的url存在
        response = self.client.get('/articles/editor/')
        #print(response.content)
        '''
        因為我們在Quikok的url那邊設定如果是不存在的urls，
        一律都會導回首頁，導致理應出不來的連線也能回傳status_code==200，
        只好記得要用其他方式做測試。
        '''
        self.assertIn('文章編輯器', str(response.content, 'utf8'), str(response.content, 'utf8'))


    def test_editor_function_receive_data(self):
        # 測試收得到資料
        data = {
            'title': 'title_test',
            'textarea': 'contents_test',
            'author_id': '0',
            'category': 'category_test',
            'hashtag': 'hashtag_test'
        }
        response = self.client.post('/articles/editor/', data=data)
        #print(response.content)
        
        self.assertIn('已經成功匯入資料庫', str(response.content, 'utf8'), str(response.content, 'utf8'))


    def test_editor_function_receive_data_and_save_in_DB(self):
        # 測試收到資料後會存進資料庫
        data = {
            'title': 'title_test',
            'textarea': 'contents_test',
            'author_id': '0',
            'category': 'category_test',
            'hashtag': 'hashtag_test'
        }
        response = self.client.post('/articles/editor/', data=data)
        
        self.assertEqual(
            article_info.objects.all().count(),
            1
        )

        
        print(article_info.objects.values())
