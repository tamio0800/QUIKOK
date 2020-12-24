from django.contrib.auth.models import User
from chatroom.models import *

# 與mr.q建立聊天室的程式碼
for i in range(51,74):
    user=User.objects.get(id = i)
    chatroom_info_Mr_Q2user.objects.create(user_auth_id= user.id,user_type= 'teacher',system_user_auth_id=50,chatroom_type='system2teacher')

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
        