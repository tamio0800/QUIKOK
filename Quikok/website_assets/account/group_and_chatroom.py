from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from account.models import student_profile, teacher_profile
from django.contrib.auth.models import Permission, User
# 這個檔案是由於起初建立的第一批假user沒有建立group,
# 使用這邊的代碼利用shell將他們加上group
# 由於 group使用上有些特殊之處因此留在這邊

# 把某個會員加進user_groups的方式
for a in User.objects.all():
    a.groups.add(id =1)

for i in range(51,52):
    user = User.objects.get(id = i)
    print(user)
    user.groups.add(2)

# 取得a屬於那些user_groups的方式
a = User.objects.get(id=1)
a.groups.first() # group特殊之處在不能直接找查必須這樣反查
a.groups.all()
for s in student_profile.objects.all():
    chatroom_info_Mr_Q2user.objects.create(user_auth_id=s.auth_id, user_type= 'student',system_user_auth_id = 404, chatroom_type='system2student')

for t in teacher_profile.objects.all():
    chatroom_info_Mr_Q2user.objects.create(user_auth_id=t.auth_id, user_type= 'teacher',system_user_auth_id = 404, chatroom_type='system2teacher')

# 測試 permission相關的table
a = User.objects.get(id=1)
a.user_permissions.all() # 對應到 user_suer_permissions