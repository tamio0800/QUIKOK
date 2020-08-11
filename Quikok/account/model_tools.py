from account.models import dev_db, user_profile
from django.contrib.auth.models import User


class user_db_manager:
    def __init__(self):
        pass
    
    def create_user(self, **kwargs):
        if kwargs['user_type'] == 'user':
            if not user_profile.objects.filter(username=kwargs['username']).count():
                # 沒有重複的username
                user_profile(
                    username = kwargs['username'],
                    password = kwargs['password_hash'],
                    name = kwargs['name'],
                    nickname = kwargs['nickname'],
                    birth_date = kwargs['birth_date'],
                    is_male = kwargs['is_male'],
                    role = kwargs['role'],
                    mobile = kwargs['mobile'],
                    picture_folder = kwargs['picture_folder'],
                    update_someone_by_email = kwargs['update_someone_by_email'],
                ).save()
                print(kwargs['username'], 'has been created.')

                # 複寫到auth User中
                User(
                    username = kwargs['username'],
                    password = kwargs['password_hash'],
                    is_superuser = 0,
                    first_name = '',
                    last_name = '',
                    email = '',
                    is_staff = 0,
                    is_active = 1,
                ).save()
                return True
            else:
                return False
        elif kwargs['user_type'] == 'vendor':
            pass

    def dev_create_user(self, **kwargs):
        if kwargs['user_type'] == 'user':
            if not dev_db.objects.filter(username=kwargs['username']).count():
                # 沒有重複的username
                dev_db(
                    username = kwargs['username'],
                    password = kwargs['password'],
                    name = kwargs['name'],
                    birth_date = kwargs['birth_date'],
                    is_male = kwargs['is_male'],
                ).save()
                print(kwargs['username'], 'has been created.')
                return True
            else:
                return False
        elif kwargs['user_type'] == 'vendor':
            pass
    