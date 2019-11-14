from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    participants = models.ManyToManyField(User, blank=True)

    def __str__(self):
       query_set = self.participants.all()
       return f"{query_set[0]},{query_set[1]}"

class Message(models.Model):
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    recipient = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    message_body = models.TextField(blank=False, default="", max_length=100)
    date_time = models.DateTimeField(auto_now_add=True)
    chat_session = models.ForeignKey(Chat, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
       return f"{self.author.username}->{self.recipient.username}"

