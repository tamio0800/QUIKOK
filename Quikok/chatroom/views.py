from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from .models import Messages, chat_room


# Create your views here.


def chat(request, user_url):
    user=User.objects.get(username= user_url)
    
    username=user.username
    
    room_list=chat_room.objects.filter(Q(member1=user)|Q(member2=user)).order_by("-date")
    room=''
    chat_messages=''
    print('\n\nrequest.GET:'+str(request.GET))
    if 'room_id' in request.GET:
        room_id=request.GET['room_id']
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
        'chatroom':room
    })
