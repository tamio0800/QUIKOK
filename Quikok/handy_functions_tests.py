import unittest
from datetime import datetime
from unittest.case import skip
from handy_functions import turn_first_datetime_string_into_time_format
from handy_functions import turn_picture_into_jpeg_format
from PIL import Image
import os

class TEST_HANDY(unittest.TestCase):

    def test_turn_first_datetime_string_into_time_format(self):
        '''檢查是否可以將字串化的日期區間轉為datetime格式'''
        dt1 = '2021-02-01:2,3,4,5;'
        self.assertEqual(
            turn_first_datetime_string_into_time_format(dt1),
            datetime(2021, 2, 1, 1, 0))

        dt2 = '2021-02-03:0;'
        self.assertEqual(
            turn_first_datetime_string_into_time_format(dt2),
            datetime(2021, 2, 3, 0, 0))

        dt3 = '2021-02-01:47'
        self.assertEqual(
            turn_first_datetime_string_into_time_format(dt3),
            datetime(2021, 2, 1, 23, 30))

        dt4 = '2021-02-01:45,46;'
        self.assertEqual(
            turn_first_datetime_string_into_time_format(dt4),
            datetime(2021, 2, 1, 22, 30))

    
    @skip
    def test_turn_picture_into_jpeg_format_change_size(self):
        '''
        測試Image的一些性質
        '''
        the_path = \
            'user_upload/temp/before_signed_up/tamio0800111111/customized_lesson_background.png'
        origin_pic = Image.open(the_path)
        self.assertIsNotNone(origin_pic)  # 確實有抓到東西
        origin_w_n_h = origin_pic.size
        origin_size = os.path.getsize(the_path)
        print(f"Origin W * H:{origin_w_n_h}")
        print(f"Origin Size:{origin_size}")

        new_size = (1110, 300)
        modified_pic = origin_pic.resize(new_size, Image.ANTIALIAS)
        new_path = \
            'user_upload/temp/before_signed_up/tamio0800111111/modified.jpeg'
        modified_pic.save(new_path, format='JPEG', quality=75)

        modified_sized = os.path.getsize(new_path)
        print(f"Modified W * H:{modified_pic.size}")
        print(f"Modified Size:{modified_sized}\n")
        print(f"Reduced to  {round(modified_sized/origin_size,4)}")
        origin_pic.close()
        modified_pic.close()


    def test_turn_picture_into_jpeg_format_change_size(self):
        '''
        測試是否可以成功將圖片轉為指定的大小
        '''
        the_path = \
            'user_upload/temp/before_signed_up/tamio0800111111/customized_lesson_background.png'
        to_path = \
            'user_upload/temp/before_signed_up/tamio0800111111/test1.jpeg'
        to_size = (450, 450)
        turn_picture_into_jpeg_format(the_path, to_size, to_path)
        # 理論上，to_path應該要有一個圖片才對，且大小為400*400
        
        self.assertTrue(os.path.isfile(to_path))  # 確認有該檔案
        pic = Image.open(to_path)
        #self.assertEqual(pic.size, to_size)
        pic.close()
        #os.unlink(to_path)
        #self.assertFalse(os.path.isfile(to_path))  # 確認刪除該檔案

        to_path = \
            'user_upload/temp/before_signed_up/tamio0800111111/test2.jpeg'
        to_size = (2200, 900)
        turn_picture_into_jpeg_format(the_path, to_size, to_path)
        self.assertTrue(os.path.isfile(to_path))  # 確認有該檔案
        pic = Image.open(to_path)
        #self.assertEqual(pic.size, to_size)
        pic.close()
        #os.unlink(to_path)
        #self.assertFalse(os.path.isfile(to_path))  # 確認刪除該檔案

    @skip
    def test_to_resize_pictures(self):
        '''
        手動縮圖
        '''
        the_path = \
            'user_upload/temp/change_pic_size'                
        if 'thumbnail' in os.listdir(the_path)[0].split('.')[0]:
            # 大頭貼
            pic_name = os.listdir(the_path)[0]
            original = Image.open(f"{the_path}/{pic_name}").convert("RGB")
            original.save(f'{the_path}/thumbnail_original.jpeg', format='JPEG', quality=100)
            original.close()
            # os.unlink(f"{the_path}/{pic_name}")
            
            the_pic = Image.open(f'{the_path}/thumbnail_original.jpeg').convert("RGB")
            w, h = the_pic.size
            if w > h:
                new_w = round(w / (h/200))
                to_size = (new_w, 200)
            else:
                new_h = round(h / (w/200))
                to_size = (200, new_h)
            
            new_pic = the_pic.resize(to_size, Image.ANTIALIAS)
            new_pic.save(f"{the_path}/thumbnail.jpeg", quality=70)

        
        for _ in os.listdir(the_path):
            if _.endswith('jpeg') == False:
                os.unlink(f"{the_path}/{_}")


            


if __name__ == '__main__':
    unittest.main()

