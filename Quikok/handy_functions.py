from datetime import date, datetime
import os
from PIL import Image


def price_round(number, digits):
     # digit 不要小於第五位
    return round(number + 0.00001, digits)

def check_if_all_variables_are_true(*args):
    '''
    確認所有變數皆不為否
    '''
    for i, each_arg in enumerate(args):
        if each_arg == False:
            print(f"{i}: {each_arg}")
            return False
    return True

def sort_dictionaries_in_a_list_by_specific_key(specific_key, followed_by_values_in_list, the_list):
    '''
    假設有一list長這樣：[dict1, dict2, dict3, dict4...]，
    此函數會按照dict中的某個key values將此list重新排序。
    '''
    _new_mapping_dict = dict()
    for each_dict in the_list:
        _new_mapping_dict[
            each_dict[specific_key]
        ] = each_dict
    _data = list()
    for each_value in followed_by_values_in_list:
        _data.append(_new_mapping_dict[each_value])
    
    return _data


def is_num(target):
    try:
        int(target)
        if int(target) == float(target):
            return True
        else:
            return False
    except:
        return False


def clean_files(folder_path, key_words):
    for each_file in os.listdir(folder_path):
        if key_words in each_file:
            os.unlink(os.path.join(folder_path, each_file))


def date_string_2_dateformat(target_string):
    from datetime import date as date_function
    if not target_string == False:
        try:
            # 將前端的 2000-01-01格式改為20000101
            nodash_str = target_string.replace('-','')
            if len(nodash_str) == 8 :
                _year, _month, _day = int(nodash_str[:4]), int(nodash_str[4:6]), int(nodash_str[-2:])
                return date_function(_year, _month, _day)
            else:
                return False
        except Exception as e:
            print(e)
            return False
    else:
        return False

def clean_files(folder_path, key_words):
    '''
    自動搜尋folder_path所有的檔案，
    並且刪除包含key_words關鍵字的檔案。
    '''
    for each_file in os.listdir(folder_path):
        if key_words in each_file:
            os.unlink(os.path.join(folder_path, each_file))


def split_non_continuous_times(times_as_string):
    # times_as_string >> 1,2,3,6,7,8 >> 1,2,3 & 6,7,8
    num_as_int_in_list = [int(_) for _ in times_as_string.split(',')]
    num_of_elements = len(num_as_int_in_list)
    
    if num_of_elements == 0:
        return ['',]
    elif num_of_elements == 1:
        return [times_as_string,]
    else:
        _temp_list_of_lists = list()
        _temp_list = list()
        
        for i, element in enumerate(num_as_int_in_list[:-1]):
            # 預留1位數的空間
            if abs(element-num_as_int_in_list[i+1]) == 1:
                _temp_list.append(str(element))
            else:
                _temp_list.append(str(element))
                _temp_list_of_lists.append(','.join(_temp_list))
                _temp_list = list()
        
        if len(_temp_list):
            # 有東西
            _temp_list.append(str(num_as_int_in_list[-1]))
            _temp_list_of_lists.append(','.join(_temp_list))
        
        if str(num_as_int_in_list[-1]) not in ','.join(_temp_list_of_lists):
            _temp_list_of_lists.append(str(num_as_int_in_list[-1]))
        
        return _temp_list_of_lists


def booking_date_time_to_minutes_and_cleansing(the_booking_date_time):
        '''
        將收到的 booking_date_time，清理後回傳：
        (
            1. 總共預約了多少分鐘, 
               去除空堂如「%Y-%m-%d:;」後的真正有意義的預約時段，以字典的方式回傳。
            2. 將諸如 2020-01-01:1,2,3,6,7,8; 的預約 拆成：
               2020-01-01:1,2,3;
               2020-01-01:6,7,8;
        )
        '''
        _temp_dict = dict()
        splited_clean_date_time = list()
        time_count = 0
        for each_booking_time in the_booking_date_time.split(';'):
            if len(each_booking_time) > 11:

                the_date, the_time = each_booking_time.split(':')
                times_list = list()

                for each_splited_time in split_non_continuous_times(the_time):
                    time_count += len(each_splited_time.split(','))
                    times_list.append(each_splited_time)

                _temp_dict[the_date] = times_list
            
        #print(f'the_booking_date_time  {(the_booking_date_time, time_count*30, _temp_dict)}')
        return (time_count*30, _temp_dict)

def turn_date_string_into_date_format(target_string):
    '''
    將 yyyy-mm-dd 的 string 轉化為 date 的形式
    '''
    y, m, d = target_string.split('-')
    return date(year=int(y), month=int(m), day=int(d))


def turn_current_time_into_time_interval():
    current_time = datetime.now()
    # 0 > 00:00 - 00:30
    # 1 > 00:30 - 01:00
    # 2 > 01:00 - 01:30
    # 3 > 01:30 - 02:00
    # 4 > 02:00 - 02:30
    # .................
    # 46: 23:00 - 23:30
    # 47: 23:30 - 24:00
    # 00 >> 0, 1; 
    # 01 >> 2, 3;
    # 02 >> 4, 5;
    # 03 >> 6, 7;
    # ...........
    # 23 >> 46, 47
    # current_hour >> (current_hour*2, current_hour*2+1)
    if current_time.minute > 30:
        return current_time.hour * 2 + 1
    else:
        return current_time.hour * 2


def turn_first_datetime_string_into_time_format(datetime_string):
    '''
    這是為了將如 2020-01-01:1,2,3:
         "2020-01-01:0,1,2;" 轉換成 >> 2020-01-01 00:00，
         ""2020-01-01:3,4;" >> 2020-01-01 01:30，
         ""2020-01-01:2;" >> 2020-01-01 01:00
    的函式。
    '''
    datetime_string = datetime_string.replace(';', '')
    date_string, time_string = datetime_string.split(':')

    _year, _month, _day = [int(_) for _ in date_string.split('-')]
    first_element = int(time_string.split(',')[0])

    the_quotient = int(first_element / 2)
    remainder = first_element % 2

    if remainder == 0:
        return datetime(_year, _month, _day, the_quotient, 0)
    else:
        return datetime(_year, _month, _day, the_quotient, 30)


def bound_number_string(target_number_string, min=1, max=5):
    '''
    將超出範圍外的數值限定在不超過範圍的極端值，如果為空字串的話則回傳None.
    '''
    if len(target_number_string) == 0:
        return None
    elif int(target_number_string) > max:
        return max
    elif int(target_number_string) < min:
        return min
    else:
        return int(target_number_string)


def return_none_if_the_string_is_empty(target_string):
    '''
    若該變數為空字串，則回傳None，反之回傳原來的值
    '''
    if len(target_string.strip()) == 0:
        return None
    else:
        return target_string


def get_lesson_s_best_sale(lesson_object):
    '''
    用來取得該門課程最優惠/吸引人的標語
    '''
    # lesson_object = lesson_info.objects.filter(id=lesson_id).first()
    trial_class_price = lesson_object.trial_class_price
    price_per_hour = lesson_object.price_per_hour
    if trial_class_price != -999 and trial_class_price < price_per_hour:
        # 有試教優惠的話就直接回傳
        return "試課優惠"
    else:
        discount_price = lesson_object.discount_price
        discount_pairs = discount_price.split(';')
        all_discounts = [int(_.split(':')[-1]) for _ in discount_pairs if len(_) > 0]
        if len(all_discounts) == 0:
            # 沒有折數
            return ''
        else:
            best_discount = min(all_discounts)
            return str(100 - best_discount) + '% off'
            # 反之則回傳  xx% off


def get_teacher_s_best_education_and_working_experience(teacher_object):
    '''
    這個用來取得最適合呈現的，老師的「學歷」與「經歷」，以及這兩者的認證情況。
    '''
    # teacher_object = teacher_profile.objects.get(auth_id=teacher_auth_id)
    
    first_exp, second_exp = '', ''  # 第一個與第二個要回傳的東西
    is_first_one_approved, is_second_one_approved = False, False  # 第一個與第二個要回傳的東西是否有經過認證
    
    if teacher_object.education_1 != '':
        # 老師的 education_1 有值，理論上應該要有啦!
        first_exp = teacher_object.education_1
        is_first_one_approved = teacher_object.education_approved
    elif teacher_object.education_2 != '':
        # 老師的 education_1 沒有值，檢查第二學歷
        first_exp = teacher_object.education_2
        is_first_one_approved = teacher_object.education_approved
    elif teacher_object.education_3 != '':
        # 老師的 education_2 沒有值，檢查第三學歷
        first_exp = teacher_object.education_3
        is_first_one_approved = teacher_object.education_approved
    elif teacher_object.company != '':
        first_exp = teacher_object.company
        is_first_one_approved = teacher_object.work_approved
    elif teacher_object.special_exp != '':
        first_exp = teacher_object.special_exp
        is_first_one_approved = teacher_object.other_approved

    if first_exp != '':
        # 已經找到第一欄位了
        if teacher_object.company != '' and first_exp != teacher_object.company:
            # 開始找第二欄位，先看原本的工作有沒有值
            second_exp = teacher_object.company
            is_second_one_approved = teacher_object.work_approved
        elif teacher_object.education_2 != '' and first_exp != teacher_object.education_2:
            # 工作沒有值，但是第二學歷有值，用第二學歷
            second_exp = teacher_object.education_2
            is_second_one_approved = teacher_object.education_approved
        elif teacher_object.special_exp != '' and first_exp != teacher_object.special_exp:
            # 第二學歷也沒有值，用特殊經歷作為工作
            second_exp = teacher_object.special_exp
            is_second_one_approved = teacher_object.other_approved
        elif teacher_object.education_3 != '' and first_exp != teacher_object.education_3:
            # 特殊經歷也沒有值，但是第三學歷有值，用第三學歷
            second_exp = teacher_object.education_3
            is_second_one_approved = teacher_object.education_approved

    return (first_exp, second_exp, is_first_one_approved, is_second_one_approved)


def turn_picture_into_jpeg_format(picture_path, to_size, to_path, quality=70):
    '''
    將圖片轉成指定的大小 to_size:(height * width)，並存至指定的位置，大小如下：
        (*)課程背景圖
        尺寸：1110*300(PX)
        容量：50KB

        (*)課程小卡圖
        尺寸；516*240(PX)
        容量：因為會在首頁出現越小越好

        (*)大頭照
        尺寸：200*200(PX)
        容量；45KB

    當用戶上傳的圖片不符合上述比例時，一律先填補到符合該比例，再縮小或放大，
    當比例誤差在5%以內時，都算符合比例好了。
    '''
    original_pic = Image.open(picture_path).convert("RGB")
    # 確認一下目前長寬比例與目標長寬比例的差距
    origin_w, origin_h = original_pic.size
    target_w, target_h = to_size[0], to_size[1]
    
    # 取的比原來要的還更大，這樣才不會邊緣留空不好看。
    # 假設要將某圖resize成 200*200，若原圖為 400*300，則變成 267*200，
    # 假設要將某圖resize成 200*100，若原圖為 400*300，則變成 >> 200*150；
    # 假設要將 400*300 放大為 1100*600，此時則為 1100*825。
    current_w_h_ratio = origin_w / origin_h
    new_w_h_ratio = target_w / target_h

    if new_w_h_ratio > current_w_h_ratio:
        # 代表其 width 比例更高，應該以目前的 width 對準新比例的 width
        new_w = target_w
        new_h = round(origin_h * target_w / origin_w)
    else:
        new_w = round(origin_w * target_h / origin_h)
        new_h = target_h

    to_size = (new_w, new_h)
    new_pic = original_pic.resize(to_size, Image.ANTIALIAS)
    new_pic.save(to_path, format='JPEG', quality=quality)
    original_pic.close()


def handy_round(origin_number, digits=0):
    '''因為python中，四捨五入0.5會變成0，故寫一個不會造成這個結果的方法的方法'''
    modification = 1 / 10**(digits+2)
    if origin_number > 0:
        return round(origin_number + modification, digits)
    elif origin_number < 0:
        return round(origin_number - modification, digits)
    else:
        return 0

