from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, CreateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Chat, Message
from .forms import NewMessageForm
from operator import attrgetter


class PrivateMessagesListView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'chat/chat_list_window.html'

    def get_queryset(self):
        queryset = dict()
        private_chat = Chat.objects.filter(participants__pk=self.request.user.pk)
        for chat in private_chat.all():
            last_message = Message.objects.filter(chat_session=chat)

            chat_participant = chat.__str__()
            user_index = chat_participant.rfind(self.request.user.username)

            if user_index == 0:
                user_index = 1
            else:
                user_index = 0

            chat_participant = chat_participant.split(",")
            chat_participant = User.objects.get(username=chat_participant[user_index])
            queryset[chat_participant] = last_message.all().last()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PrivateMessagesListView, self).get_context_data(**kwargs)
        context['chat_list'] = self.get_queryset()

        return context

class ChatWindowListView(LoginRequiredMixin, ListView, CreateView):
    model = Chat
    template_name = 'chat/chat_window.html'

    def get_context_data(self, **kwargs):
        chat_participant = User.objects.filter(username=self.kwargs['user']).first()
        chat_session = Chat.objects.filter(participants=chat_participant).filter(participants=self.request.user)

        try:
            user_to_recipient = Message.objects.filter(author=self.request.user, recipient=chat_participant, chat_session=chat_session.all().first())
            user_to_recipient = list(user_to_recipient.all())
        except ObjectDoesNotExist:
            user_to_recipient = []
        
        try:
            recipient_to_user = Message.objects.filter(author=chat_participant, recipient=self.request.user, chat_session=chat_session.all().first())
            recipient_to_user = list(recipient_to_user.all())
        except ObjectDoesNotExist:
            recipient_to_user = []
        
        messages_list = sorted(user_to_recipient + recipient_to_user, key = attrgetter('date_time') )

        paginator = Paginator(messages_list, 20) 

        if 'page' in self.request.GET:
            page =  self.request.GET.get('page')
        else:
            page = paginator.num_pages

        messages_list = paginator.get_page(page)

        context=dict(messages_list=messages_list, recipient=chat_participant, form=NewMessageForm)

        return context

    def post(self, request, *args, **kwargs):

        sender = self.request.user
        try:
            recipient = User.objects.get(username=self.kwargs['user'])
        except ObjectDoesNotExist:
            print("error...")

        new_message = None
      
        if sender.username != recipient.username:
            chat_object = Chat.objects.filter(participants=sender).filter(participants=recipient).first()
 
            new_message = Message.objects.create(author=sender, recipient=recipient, message_body=request.POST['message_body'], \
                                                 chat_session=chat_object)
            
            if chat_object == None:
                chat_object = Chat.objects.create()
                chat_object.participants.set([sender, recipient])
                chat_object.save()
                new_message.chat_session = chat_object
        
        new_message.save()

        return redirect ('chat:chat-window', recipient)

class ChatWindowDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Chat
    template_name = 'chat/chat_confirm_delete.html'
    success_url = reverse_lazy('private_messages')

    def test_func(self):
        chat = self.get_object()
      
        if self.request.user in chat.participants.all():
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(ChatWindowDeleteView, self).get_context_data(**kwargs)
        recipient = User.objects.filter(username=self.kwargs['user']).first()

        context=dict(recipient=recipient)
        
        return context

    def get_object(self, queryset=None):
        chat_participant = User.objects.filter(username=self.kwargs['user']).first()
        chat_session = Chat.objects.filter(participants=chat_participant).filter(participants=self.request.user).first()

        return chat_session

    def post(self, request, *args, **kwargs):
       
        messages.success(request, "Your Chat Has Been Deleted")
        return self.delete(request, *args, **kwargs)

        
