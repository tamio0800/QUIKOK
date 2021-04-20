# 這邊放的是最早期版本的聊天室寫法, 2020年9月左右
'''
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
                #print("測試"+ str(friend_temp.picture_folder.url))
                thumb_nail_list.append(friend_temp.thumbnail_dir)
            ###    print(friend_temp.picture_folder)
                
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
                print("加了一個學生到好友名單:"+ friend_temp.nickname)
                friend_nick_list.append(friend_temp.nickname)
                roomid_list.append(room.id)
                thumb_nail_list.append(friend_temp.thumbnail_dir)
            else:    
                print("好友:"+ room.student.username + "不是老師也不是學生，可能是測試帳號或漏加帳號")    
            #else:
            #    friend_nick_temp = teacher_profile.objects.get(username= room.student.username)
            #    friend_nickname = friend_nick_temp.nickname
            #    friend_list.append(friend_nickname)
            #    roomid_list.append(room.id)

    for friend in friend_nick_list:
        print('好友暱稱表:'+ friend)
    ###print(thumb_nail_list)
        
    roomid_and_friend_list = zip(roomid_list, friend_nick_list, thumb_nail_list)
    ###roomid_and_friend_list = zip(roomid_list, friend_nick_list)
    # 將房間id, 好友暱稱, 大頭貼資訊給前端
    

    # 當前聊天內容(畫面左側)與對方資訊(右側)
    room=''
    chat_messages=''
    print('\n\nrequest.GET:'+str(request.GET))
    if 'room_id' in request.GET:
        room_id = request.GET['room_id']
        room=chat_room.objects.get(id=room_id)
        if room.student.username == username:
            current_user_identity = 'student'
            current_teacher = teacher_profile.objects.get(username = room.teacher.username)
            current_student = ''
        else:
            current_user_identity = 'teacher'
            current_student = student_profile.objects.get(username = room.student.username)
            current_teacher = ''
        #else: annie:0825 現在student_profile學生尚未有intro欄位 
        #    current_student = student_profile.objects.get(username = room.student.username) 
           
        #print("hi" +room.student.username)

        if room in room_list:
            chat_messages = Messages.objects.filter(group=room_id).order_by("timestamp")[:100] #前一百則聊天訊息

        else :
            room=''
    else :
        print('沒有收到房間id')

    print('\n\ncurrent_user:\n'+str(user))
    print('\n\nchat_messages:\n'+str(chat_messages))
    print('\n\nroom_list:\n'+str(room_list))
    return render(request, 'chatroom/room.html', {
        'current_user':user,
        'chat_messages': chat_messages,
        'room_list': room_list,
        'chatroom':room,
        'current_teacher':current_teacher,
        'current_student':current_student,
        'current_user_identity': current_user_identity,
        'roomid_and_friend_list':roomid_and_friend_list,
    })
    '''
# 這個是測試接收WS的過程...

    def connect_2(self):
        print('成功!')
        print('\n\nconnect_info:\n'+str(self.scope)+'\n\n')
        # 當用戶上線就建立所有它在info裡面的連線, 加入同一個group
        # 這種作法需要前端丟變數來讓我知道是要建立連線還是只是聊
        # add connection to existing groups
        userID = self.scope["url_route"]["kwargs"]["room_url"].split('_')[0]
        user_type = auth_ckeck.check_user_type(userID)
        if user_type == 'teacher':
            for friend_room in chatroom_info_user2user.objects.filter(teacher_auth_id=userID):
                async_to_sync(self.channel_layer.group_add)(friend_room.id, self.channel_name)

        # 接收格式 'kwargs': {'room_url': '204_chatroom_4_0'}
        if self.scope["url_route"]["kwargs"]["room_url"].split('_')[3] == '0':
            self.room_group_name = self.scope["url_route"]["kwargs"]["room_url"].split('_')[2]
            self.chatroom_type = 'user2user'
        # 系統與user接收格式 'kwargs': {'room_url': '204_chatroom_4_1'}
        elif self.scope["url_route"]["kwargs"]["room_url"].split('_')[3] == '1':
            self.room_group_name = self.scope["url_route"]["kwargs"]["room_url"].split('_')[2]
            #self.room_group_name = 'system'+ str(self.scope["url_route"]["kwargs"]["room_url"].split('_')[2])
            self.chatroom_type = 'system2user'
            # 測試對一個使用者來說, self變數是否會留存,還是我得另存db
            self.system_room_group_name = copy.deepcopy(self.room_group_name)
            print(type(self.room_group_name))
        else: #以後聊天室如果有更多種類可以加這
            pass
        print('channel name:')
        print(self.channel_name)
        print('room_group_name')
        print(self.room_group_name)
        
        # Join room group
        # 目前我不確定用for loop來做時,是否自是將各channel加入這個group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name)
        self.accept()
        # 如果是系統連線,此時要存到記憶體中
        print('websocket connect success')