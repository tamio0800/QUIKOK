from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password  # 這一行用來加密密碼的
from .model_tools import user_db_manager

# Create your views here.
def signup(request):
    title = '開課! Quikok - 會員註冊'
    
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password_hash = make_password(request.POST['password'])
        name = request.POST['name'].strip()
        nickname = request.POST['nickname'].strip()
        birth_date = request.POST['birth_date']
        is_male = request.POST['is_male']
        role = request.POST['role']
        mobile = request.POST['mobile'].strip()
        picture_folder = 'to_be_deleted'
        update_someone_by_email = request.POST['update_someone_by_email'].strip()

        db_manager = user_db_manager()        
        ret = \
            db_manager.create_user(
                user_type = 'user',
                username = username,
                password_hash = password_hash,
                name = name,
                nickname = nickname,
                birth_date = birth_date,
                is_male = is_male,
                role = request.POST['role'],
                mobile = request.POST['mobile'],
                picture_folder = 'to_be_deleted',
                update_someone_by_email = request.POST['update_someone_by_email'],
            )
        if not ret:
            already_taken_username = username
        

        return render(request, 'account/user_signup.html', locals())
    return render(request, 'account/user_signup.html', locals())

def dev_signin(request):
    title = '開課! Quikok - 會員登入'
    return render(request, 'account/dev_user_signin.html', locals())


