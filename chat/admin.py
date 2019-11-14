from django.contrib import admin
from .models import Chat, Message

class ChatAdmin(admin.ModelAdmin):
   pass
    
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'message_body', 'date_time', 'chat_session']

admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)