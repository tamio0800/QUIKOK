
from Quikok.chatroom.models import Messages, chat_room
from django.contrib.auth.models import User
# Create your tests here.


if __name__ == '__main__':

  
    user1=User.objects.get(id=user1id)
    user2=User.objects.get(id=user2id)
    chat_room.objects.create(member1=user1,member2=user2)