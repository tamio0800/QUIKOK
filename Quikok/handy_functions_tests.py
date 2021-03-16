import unittest
from datetime import datetime
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

    
    def test_turn_picture_into_jpeg_format_change_size(self):
        '''
        測試是否可以成功將圖片轉為指定的大小
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


if __name__ == '__main__':
    unittest.main()

