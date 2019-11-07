from django.db import models
from django.contrib.auth.models import User


class Forum(models.Model):
    name = models.CharField(max_length=40, blank=False)
    moderator = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

class ForumCategory(models.Model):
    name = models.CharField(max_length=40, blank=False)
    forums = models.ManyToManyField(Forum, blank=True)

    def __str__(self):
        return self.name

class Post(models.Model):

    POST_TYPE = (
        ('normal', 'normal'),
        ('pinned', 'pinned'),
    )

    author = models.ForeignKey(User, default = "", on_delete=models.CASCADE, related_name='+')
    forum = models.ForeignKey(Forum,blank=True, null=True, on_delete=models.CASCADE)
    message_body = models.TextField(blank=False, default="")
    datetime = models.DateTimeField(auto_now_add=True)
    like_list = models.ManyToManyField(User, blank=True, related_name='+')
    unlike_list = models.ManyToManyField(User, blank=True, related_name='+')
    announcement = models.CharField(max_length=12, choices=POST_TYPE, default='normal')
    #image...

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.forum}-{self.author}"

class MainTopic(Post):
    title = models.CharField(max_length=50, blank=False, default="")

    def __str__(self):
        return self.title


class Comment(Post):
    thread_id = models.ForeignKey(MainTopic, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    
    def __str__(self):
        return f"{self.forum}-{self.__class__.__name__}"

class Reply(Post):
    thread_id = models.ForeignKey(MainTopic, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    reply_to_main_thread = models.ForeignKey(MainTopic, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    reply_to_comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    reply_to_older_reply = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)#    

    def __str__(self):
        return f"{self.forum}-{self.__class__.__name__}"

#Private messages 