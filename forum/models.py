from django.db import models
from django.contrib.auth.models import User





#Forum - name , moderators, number of posts , posts , forum category
class Forum(models.Model):
    name = models.CharField(max_length=40, blank=False)
    moderator = models.ManyToManyField(User, blank=True)
    #posts = models.ForeignKey(Post, blank=True, null=True, on_delete=models.CASCADE) # PROTECT, SET_NULL, SET_DEFAULT
    #number_of_posts = Post.objects.all().count()
    #forum_category = models.ForeignKey(ForumCategory)
    def __str__(self):
        return self.name

#Post - title , description, author , time, date maybe likes..., image... reply...

#Main FOrum - Forum Category
class ForumCategory(models.Model):
    name = models.CharField(max_length=40, blank=False)
    forums = models.ManyToManyField(Forum, blank=True)

    def __str__(self):
        return self.name

# Option for pinned messages, announcements
class Post(models.Model):
    author = models.ForeignKey(User,  default = "", on_delete=models.CASCADE, related_name='+')
    forum = models.ForeignKey(Forum,blank=True, null=True, on_delete=models.CASCADE)
    message_body = models.TextField(blank=False, default="")
    datetime = models.DateTimeField(default="")#auto_now=True)
    like = models.IntegerField(default=0)
    like_list = models.ManyToManyField(User, blank=True, related_name='+')
    unlike = models.IntegerField(default=0)
    unlike_list = models.ManyToManyField(User, blank=True, related_name='+')

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.forum}-{self.author}"

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})

class Comment(Post):
    #main_topic = models.ForeignKey(MainTopic, default="", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.forum}-{self.__class__.__name__}"
    # def get_queryset(self):
    #     #Post.objects.filter(author=user).order_by('-date_posted')
    #     queryset = super(Comment, self).get_queryset()
    #     # queryset = MainTopic.objects.filter(comments=self)
    #     # print(queryset)
        
    #     return queryset

class Reply(Post):
    #main_topic = models.ForeignKey(MainTopic, on_delete=models.CASCADE, related_name='+')
    #reply_to = models.ForeignKey(MainTopic or Comment, on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return f"{self.forum}-{self.__class__.__name__}"

    # def get_queryset(self):
    #     #Post.objects.filter(author=user).order_by('-date_posted')
    #     queryset = super(Reply, self).get_queryset()
    #     # queryset = MainTopic.objects.filter(replies__contains=self)
    #     print(queryset)
        
    #     return queryset

class MainTopic(Post):
    title = models.CharField(max_length=50, blank=False, default="")
    comments = models.ManyToManyField(Comment, blank=True, related_name='+')
    replies = models.ManyToManyField(Reply,blank=True, related_name='+')

    def __str__(self):
        return self.title

    def get_queryset(self):
        #Post.objects.filter(author=user).order_by('-date_posted')
        queryset = super(MainTopic, self).get_queryset()
        # queryset = MainTopic.objects.filter(replies__contains=self)
        print(queryset)
        
        return queryset



#Private messages 