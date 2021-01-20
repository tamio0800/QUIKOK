from datetime import date, datetime
import os

def check_if_all_variables_are_true(*args):
    '''
    確認所有變數皆不為否
    '''
    for each_arg in args:
        if each_arg in [False, 'False', 'false']:
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

