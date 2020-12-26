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