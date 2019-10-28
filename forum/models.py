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
    author = models.ForeignKey(User, default = "", on_delete=models.CASCADE, related_name='+')
    forum = models.ForeignKey(Forum,blank=True, null=True, on_delete=models.CASCADE)
    message_body = models.TextField(blank=False, default="")
    datetime = models.DateTimeField(default="")#auto_now=True)
    like_list = models.ManyToManyField(User, blank=True, related_name='+')
    unlike_list = models.ManyToManyField(User, blank=True, related_name='+')
    announcement = models.BooleanField(default=False)
    pinned_message = models.BooleanField(default=False)
    #image...

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.forum}-{self.author}"

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})

class Comment(Post):

    def __str__(self):
        return f"{self.forum}-{self.__class__.__name__}"


class MainTopic(Post):
    title = models.CharField(max_length=50, blank=False, default="")
    thread_posts = models.ManyToManyField(Comment, blank=True, related_name='+')
    #replies = models.ManyToManyField(Reply,blank=True, related_name='+')

    def __str__(self):
        return self.title


class Reply(Post):
    thread_id = models.ForeignKey(MainTopic, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    reply_to_main_thread = models.ForeignKey(MainTopic, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    reply_to_comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    reply_to_older_reply = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)#    

    def __str__(self):
        return f"{self.forum}-{self.__class__.__name__}"

#Private messages 