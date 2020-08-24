from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from .models import Messages, chat_room
from account.models import student_profile, teacher_profile

# Create your views here.


def chat(request, user_url):
    user = User.objects.get(username= user_url)
    username = user.username

    # 畫面上要顯示的是暱稱，先找看看user是不是老師
    user_nick_temp = teacher_profile.objects.filter(username= username)
    # 如果user不是老師, nickname會小於1，因此去學生那邊找
    if len(user_nick_temp)< 1:
        user_nick_temp = student_profile.objects.filter(username= username)
        if len(user_nick_temp)< 1:
            print("當前使用者:"+ username + "不是老師也不是學生，可能是測試帳號或漏加帳號")
        else:
            user_nick_temp = student_profile.objects.get(username= username) 
            user_is_teacher = "F" # 之後在html 依據user是學生還是老師切換顯示內容用的
    else:
        user_nick_temp = teacher_profile.objects.get(username= username)
        user_is_teacher = "T"
        user_nickname = user_nick_temp.nickname

    room_list=chat_room.objects.filter(Q(student=user.id)|Q(teacher=user.id)).order_by("-date")

# 以下為左邊好友列表顯示暱稱用
# 用room_list的member id 找到對應的 auth_username
# 再用 auth_username 去 account的兩個table找 nickname
    friend_nick_list = [] #好友暱稱表
    roomid_list = [] # 聊天室 id
    thumb_nail_list = [] # 大頭貼

    for room in room_list:
        if room.student.username == username:
            # user是student, 聊天對象就是teacher, 找teacher 的nick name
            friend_nick_temp = teacher_profile.objects.filter(username= room.teacher.username)
            #if len(friend_nick_temp)<1:
            #    friend_nick_temp = student_profile.objects.filter(username= room.teacher.username)
            #    if len(friend_nick_temp)<1:
            #        print("好友:"+ room.teacher.username + "不是老師也不是學生，可能是測試帳號或漏加帳號")
                    # 測試中會加一些帳號
            #    else:
            #        friend_temp = student_profile.objects.get(username= room.teacher.username)
            #        friend_list.append(friend_temp.nickname)
            #        roomid_list.append(room.id)
            #        thumb_nail.append(friend_temp.picture_folder)
            if len(friend_nick_temp) >= 1: 
                friend_temp = teacher_profile.objects.get(username= room.teacher.username)
                friend_nick_list.append(friend_temp.nickname)
                roomid_list.append(room.id)
                print(friend_temp.picture_folder)
                #thumb_nail_list.append(friend_temp.picture_folder.url)
                
            else:    
                print("好友:"+ room.teacher.username + "不是老師也不是學生，可能是測試帳號或漏加帳號")    

            # user是老師,聊天對象是學生
        else:
            friend_nick_temp = student_profile.objects.filter(username= room.student.username)
            #if len(friend_nick_temp)<1:
            #    friend_nick_temp = student_profile.objects.filter(username= room.student.username)
            #    if len(friend_nick_temp)<1:
            #        print("好友:"+ room.student.username + "不是老師也不是學生，可能是測試帳號或漏加帳號")
            if len(friend_nick_temp) >= 1:
                friend_temp = student_profile.objects.get(username= room.student.username)
                friend_nick_list.append(friend_temp.nickname)
                roomid_list.append(room.id)
                thumb_nail_list.append(friend_temp.picture_folder)
            else:    
                print("好友:"+ room.student.username + "不是老師也不是學生，可能是測試帳號或漏加帳號")    
            #else:
            #    friend_nick_temp = teacher_profile.objects.get(username= room.student.username)
            #    friend_nickname = friend_nick_temp.nickname
            #    friend_list.append(friend_nickname)
            #    roomid_list.append(room.id)

    for friend in friend_nick_list:
        print('好友暱稱表:'+ friend)
    print(thumb_nail_list)
    roomid_and_friend_list = zip(roomid_list, friend_nick_list, thumb_nail_list)
    ### 顯示大頭貼 ###
    


    room=''
    chat_messages=''
    print('\n\nrequest.GET:'+str(request.GET))
    if 'room_id' in request.GET:
        room_id = request.GET['room_id']
        room=chat_room.objects.get(id=room_id)
        if room in room_list:
            chat_messages = Messages.objects.filter(group=room_id).order_by("timestamp")[:100]

        else :
            room=''

    print('\n\ncurrent_user:\n'+str(user))
    print('\n\nchat_messages:\n'+str(chat_messages))
    print('\n\nroom_list:\n'+str(room_list))
    return render(request, 'chatroom/room.html', {
        'current_user':user,
        'chat_messages': chat_messages,
        'room_list': room_list,
        'chatroom':room,
        #'is_teacher': user_is_teacher,
        #'friend_nickname':friend_nickname,
        #'friend_list' : friend_list,
        #'roomid_list':roomid_list,
        'roomid_and_friend_list':roomid_and_friend_list,
    })
