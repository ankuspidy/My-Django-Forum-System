from django.contrib import admin
from .models import Chat, Message

class ChatAdmin(admin.ModelAdmin):
    list_display = ['author', 'recipient']
    
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'message_body', 'date_time', 'read_status']

admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)