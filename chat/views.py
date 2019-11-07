from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Chat, Message
from .forms import NewMessageForm
# from datetime import datetime as date_time
from operator import attrgetter
# from django import forms as django_forms


#TODO// add testusermixin..... it doesnt show that user is logged in
class PrivateMessagesListView(LoginRequiredMixin, ListView): #UserPassesTestMixin
    model = Chat
    template_name = 'chat/chat_list_window.html'

    def get_queryset(self):
        queryset = Chat.objects.filter( Q(author=self.request.user) | Q(recipient=self.request.user))

        query_set = queryset
        for message in queryset:
            try:
                object_to_filter = queryset.get(author=message.recipient, recipient=message.author)
                query_set = queryset.exclude(author=message.author, recipient=message.recipient)
                
            except ObjectDoesNotExist:
                continue

        #print(query_set)
        return query_set

    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super(PrivateMessagesListView, self).get_context_data(**kwargs)
        context['chat_list'] = self.get_queryset()

        ### maybe add query to filter last message for each user into a dict
        return context

class ChatWindowListView(LoginRequiredMixin, ListView, CreateView):
    model = Chat
    template_name = 'chat/chat_window.html'

    def get_context_data(self, **kwargs):       
        #context = super(ChatWindowListView, self).get_context_data(**kwargs)   
        recipient = User.objects.filter(username=self.kwargs['user']).first()

        try:
            user_to_recipient = Chat.objects.get(author=self.request.user, recipient=recipient)
            user_to_recipient = list(user_to_recipient.messages.all())
        except ObjectDoesNotExist:
            user_to_recipient = []
        
        try:
            recipient_to_user = Chat.objects.get(author=recipient, recipient=self.request.user)
            recipient_to_user = list(recipient_to_user.messages.all())
        except ObjectDoesNotExist:
            recipient_to_user = []
        
        messages_list = sorted(user_to_recipient + recipient_to_user, key = attrgetter('date_time') )
        context=dict(messages_list=messages_list, recipient=recipient, form=NewMessageForm)
        #### need to add auto-refresh....
        return context

    def post(self, request, *args, **kwargs):

        print(self.kwargs)
        sender = self.request.user
        try:
            recipient = User.objects.get(username=self.kwargs['user'])
        except ObjectDoesNotExist:
            print("error...")

        print(sender)
        print(recipient)
        new_message = None
        chat_session = None

        if sender.username != recipient.username:
            new_message = Message.objects.create(author=sender, recipient=recipient, message_body=request.POST['message_body'])
            chat_session = Chat.objects.filter( Q(author=sender, recipient=recipient) | Q(author=recipient, recipient=sender)).first()
            if chat_session == None:
                chat_session = Chat.objects.create(author=sender, recipient=recipient)

        else:
            new_message = Message.objects.create(author=recipient, recipient=sender, message_body=request.POST['message_body'])
            chat_session = Chat.objects.filter(author=recipient, recipient=sender).first()
            if chat_session == None:
                chat_session = Chat.objects.create(author=recipient, recipient=sender)
        
        chat_session.messages.add(new_message)
        new_message.save()
        chat_session.save()

        return redirect ('chat:chat-window', recipient)