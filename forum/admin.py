from django.contrib import admin
from .models import ForumCategory, Forum, MainTopic, Comment, Reply


class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name'] 

class ForumAdmin(admin.ModelAdmin):
    list_display = ['name'] 

class MainTopicAdmin(admin.ModelAdmin):
    list_display = ['forum', 'title', 'author', 'datetime']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['forum', 'author']

class ReplyAdmin(admin.ModelAdmin):
    list_display = ['forum', 'author']

admin.site.register(ForumCategory, ForumCategoryAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(MainTopic, MainTopicAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)