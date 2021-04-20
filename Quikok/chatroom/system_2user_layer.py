# 功用:
# 1.為了讓系統可以即時發送通知給user, ex:預約通知
# 2.處理特殊情況:老師正在線上、又正好有一個新學生發msg給他，
# 如果老師沒有重新連線，由於他與該聊天室還沒有連線，所以不會收到通知、
# 需要透過系統與老師先建立的連線來通知

class layer_info_maneger:
#用來管理 system與user的channel_layer物件
    def __init__(self):
        self.channel_layer_info = dict()

    def add_layer_info(self,userID, channel_layer):
        self.channel_layer_info[userID] = channel_layer 
        print('寫入channel_layer資訊')

    def del_layer_info(self,userID):
        self.channel_layer_info.pop(userID)
        print('成功刪除channel_layer資訊')
    
    def show_channel_layer_info(self,userID):
        return(self.channel_layer_info[userID])