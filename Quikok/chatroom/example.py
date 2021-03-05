'''
from django.contrib.auth.models import User
from chatroom.models import *

# 與mr.q建立聊天室的程式碼
from chatroom.models import chatroom_info_Mr_Q2user,chatroom_history_Mr_Q2user
from account.models import student_profile, teacher_profile
for user in User.objects.all():
    find_t = teacher_profile.objects.filter(auth_id = user.id)
    find_s = teacher_profile.objects.filter(auth_id = user.id)
    if find_t.count() > 0:
        chatroom_info_Mr_Q2user.objects.create(user_auth_id=user.id, user_type='teacher',system_user_auth_id=1,chatroom_type='system2teacher')
    
    else:
        chatroom_info_Mr_Q2user.objects.create(user_auth_id=user.id, user_type='student',system_user_auth_id=1,chatroom_type='system2student')
'''

# 新增2筆user與系統的訊息
#import os
#os.chdir(r'/mnt/c/Users/st350/Desktop/QUIKOK')
#from chatroom.models import chatroom_info_Mr_Q2user,chatroom_history_Mr_Q2user
#from account.models import student_profile, teacher_profile
from datetime import datetime
from django.contrib.auth.models import User
from chatroom.models import chatroom_info_Mr_Q2user, chat_history_Mr_Q2user
# 產生目前所有user與系統聊天室的兩筆對話紀錄
def batch_create_chatrooms_for_users():
    all_auth_user_ids = list(User.objects.values_list('id', flat=True))
    authID_already_has_welcom_msg = list(chat_history_Mr_Q2user.objects.values_list('user_auth_id', flat=True))
    all_auth_user_ids.remove(1)
    all_auth_user_ids.remove(8)
    try:
        for each_auth_user_id in all_auth_user_ids: # 1是系統本身所以不要產生與1的對話紀錄
            if each_auth_user_id not in authID_already_has_welcom_msg:
                get_roomID = chatroom_info_Mr_Q2user.objects.get(user_auth_id=each_auth_user_id)
                first_system_msg = chat_history_Mr_Q2user.objects.create(
                    chatroom_info_system2user_id = get_roomID.id,
                    system_user_auth_id = 1,
                    user_auth_id = each_auth_user_id,
                    message = '於'+ datetime.now().strftime('%H:%M') +'創立聊天室',
                    message_type = 'auto_system_msg', 
                    who_is_sender = 'system',
                    sender_auth_id = 1,
                    system_is_read = True,
                    user_is_read = False)
                print(f'create system2user {each_auth_user_id} 1st msg.')
                welcom_system_msg = chat_history_Mr_Q2user.objects.create(  
                    chatroom_info_system2user_id = get_roomID.id,
                    system_user_auth_id = 1,
                    user_auth_id = each_auth_user_id,
                    message = '嗨！我是Quikok！開課的客服專家QQ球雀，有建議或是網站問題回報都可以找我唷！啾啾～',
                    message_type = 'text_msg' ,
                    who_is_sender = 'system' ,
                    sender_auth_id = 1,
                    system_is_read = True,
                    user_is_read = False)
                print(f'create system2user {each_auth_user_id} 2nd msg.')
   
    except:
        print(each_auth_user_id)

# 這邊放的是 views.py 裡面 def chatroom_content(request):
# 關於後端回傳聊天室歷史訊息給前端格式的範例

# data裡面的{} 是一個聊天室, [] 裡面的是一則訊息
'''
response_msg_data = { #1號聊天室
    'chatroomID' :1,
    'chatUnreadMessageQty':1,
    'chatUserID':1,
    'chatUserType': 'student',
    'chatUserName': '小明',
    'chatUserPath' : '/students/s1@s.com/thumbnail.png',
    'messageInfo':[
        {
            'senderID': 2, # 訊息發送方ID
            'messageType' : 0,
            'messageText' : '系統訊息1:哈囉~你好嗎~珍重再見',
            'systemCode':0,
            'messageCreateTime':str(datetime.now())
        },
        {
        'senderID': 2,
        'messageType' : 2,
        'messageText' : 'bookingID: 1; bookingLeesonID: 1;\
            bookingStatus: wait; bookingDate: 2020-11-11; \
            bookingTime: 13:00-15:00; \
            bookingUpdateTime: '+ str(datetime.now()),
        'systemCode':0,
        'messageCreateTime':str(datetime.now())
        }
    ]
}, # 2號聊天室
{
    'chatroomID' :2,
    'chatUnreadMessageQty':1,
    'chatUserID':3,
    'chatUserType': 'student',
    'chatUserName': '小花',
    'chatUserPath' : '/students/s00007@edony_test.com/thumbnail.jpg',
    'messageInfo':[
        {
        'senderID': 2,
        'messageType' : 0,
        'messageText' : '2號房間系統訊息1',
        'systemCode':0,
        'messageCreateTime':str(datetime.now())
        }
    ]
}'''


'''  
    #user1=User.objects.get(id = user1id)
    #user2=User.objects.get(id = user2id)
    user1=User.objects.get(id = 1)
    user2=User.objects.get(id = 2)
    
    chat_room.objects.create(member1 = user1, member2 =user2)


    for room in room_list:
        print(room.member2_id)

    for room in room_list:
        print(room.member1.username)
# 

friend_list = []
for room in room_list:
    if room.member1.username == username:
        # mem1是user, mem2就一定不是, 找mem2的nick name
        friend_nick_temp = vendor_profile.objects.filter(username= room.member2.username)
        if len(friend_nick_temp)<1:
            friend_nick_temp = user_profile.objects.filter(username= room.member2.username)
            if len(friend_nick_temp)<1:
                bprint("好友:"+ username + "不是老師也不是學生，可能是測試帳號或漏加帳號")
            else:
                friend_nick_temp = user_profile.objects.get(username= room.member2.username)
                friend_nickname = friend_nick_temp.nickname
                friend_list.append(friend_nickname)
        else:
            friend_nick_temp = vendor_profile.objects.get(username= room.member2.username)
            friend_nickname = friend_nick_temp.nickname
            friend_list.append(friend_nickname)

        
    else:
        friend_nick_temp = vendor_profile.objects.filter(username= room.member1.username)
        if len(friend_nick_temp)<1:
            friend_nick_temp = user_profile.objects.filter(username= room.member1.username)
            if len(friend_nick_temp)<1:
                print("好友:"+ username + "不是老師也不是學生，可能是測試帳號或漏加帳號")
            else:
                friend_nick_temp = user_profile.objects.get(username= room.member1.username)
                friend_nickname = friend_nick_temp.nickname
                friend_list.append(friend_nickname)
        else:
            friend_nick_temp = vendor_profile.objects.get(username= room.member1.username)
            friend_nickname = friend_nick_temp.nickname
            friend_list.append(friend_nickname)
'''


if __name__ == '__main__':
    batch_create_chatrooms_for_users()