from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from account.models import student_profile, teacher_profile
from chatroom.models import chatroom_info_Mr_Q2user

# 把某個會員加進user_groups的方式
for a in User.objects.all():
    a.groups.add(id =1)

# 取得a屬於那些user_groups的方式
a = User.objects.get(id=1)
a.groups.first()
a.groups.all()
for s in student_profile.objects.all():
    chatroom_info_Mr_Q2user.objects.create(user_auth_id=s.auth_id, user_type= 'student',system_user_auth_id = 404, chatroom_type='system2student')

for t in teacher_profile.objects.all():
    chatroom_info_Mr_Q2user.objects.create(user_auth_id=t.auth_id, user_type= 'teacher',system_user_auth_id = 404, chatroom_type='system2teacher')
