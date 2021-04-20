from django.contrib import admin
from chatroom.models import *

# Register your models here.

class ChatroomAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_time')

admin.site.register(chat_room, ChatroomAdmin)
admin.site.register(Messages, ChatroomAdmin)
admin.site.register(chatroom_info_user2user, ChatroomAdmin)
admin.site.register(chatroom_info_Mr_Q2user, ChatroomAdmin)
admin.site.register(chat_history_user2user, ChatroomAdmin)
admin.site.register(chat_history_Mr_Q2user, ChatroomAdmin)
admin.site.register(default_notifications_from_system, ChatroomAdmin)

# Register your models here.
