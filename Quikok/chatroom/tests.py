
from Quikok.chatroom.models import Messages, chat_room
from django.contrib.auth.models import User
# Create your tests here.


if __name__ == '__main__':

  
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
        