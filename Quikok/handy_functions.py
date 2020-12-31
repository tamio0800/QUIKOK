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


def booking_date_time_to_minutes_and_cleansing(the_booking_date_time):
        '''
        將收到的 booking_date_time，清理後回傳：
        (
            總共預約了多少分鐘, 
            去除空堂如「%Y-%m-%d:;」後的真正有意義的預約時段，以字典的方式回傳。
        )
        '''
        _temp_dict = dict()
        clean_booking_times = [_ for _ in the_booking_date_time.split(';') if len(_) > 11]
        time_count = 0
        for each_booking_time in clean_booking_times:
            the_date, the_time = each_booking_time.split(':')
            _temp_dict[the_date] = the_time
            time_count += len(the_time.split(','))
        return (time_count*30, _temp_dict)


