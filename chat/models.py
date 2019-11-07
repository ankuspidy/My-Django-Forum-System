from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    recipient = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    message_body = models.TextField(blank=False, default="", max_length=100)
    date_time = models.DateTimeField(auto_now_add=True)
    read_status = models.CharField(max_length=12, default=False)

    def __str__(self):
       return f"{self.author.username}->{self.recipient.username}"

class Chat(models.Model):
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    recipient = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
       return f"{self.author.username}->{self.recipient.username}"