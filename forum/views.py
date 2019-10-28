from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q

from django.contrib.auth.models import User
from .models import Forum, ForumCategory, MainTopic, Comment, Reply

from operator import attrgetter

class ForumListView(ListView):
    model = ForumCategory
    template_name = 'forum/home.html'

    def get_forums_details(self, forums_list)->dict:
            forum_details = dict()

            for forum in forums_list:
                main_topics = MainTopic.objects.filter(forum__name=forum.name).order_by('datetime')
                
                if main_topics.count() == 0:
                    forum_details[forum.name] = (0, 0, "None")
                    continue
                
                times = [ main_topics.last() ]
                comments = Comment.objects.filter(forum__name=forum.name).order_by('datetime')
                replies = Reply.objects.filter(forum__name=forum.name).order_by('datetime')
                number_of_messages = main_topics.count() + comments.count() + replies.count()

                if comments.count() != 0:
                    times.append(comments.last())
                if replies.count() != 0:
                    print(replies.last().message_body)
                    times.append(replies.last())

                last_message = sorted(times, key = attrgetter('datetime'), reverse=True)
                forum_details[forum.name] = (main_topics.count(), number_of_messages, last_message[0])
                
            return forum_details

    def get_context_data(self, **kwargs):
        context = super(ForumListView, self).get_context_data(**kwargs)

        context['forum_category'] = ForumCategory.objects.all()
        forums_list = Forum.objects.all()
        context['forum_details'] = self.get_forums_details(forums_list)

        return context

class ForumPostsListView(ListView):
    model = MainTopic
    template_name = 'forum/forum.html'
    paginate_by = 10

    def get_absolute_url(self):
        return reverse_lazy('', kwargs={'pk': self.pk})
        
    def get_queryset(self) :
        queryset = MainTopic.objects.order_by('datetime')
        return queryset

    def get_last_message(self, forum_name, main_topics)->dict:
        last_messages = dict()
        threads_replies_amount = dict()

        if main_topics.count() == 0:
            return "None"
        else:
            #total_replies = Reply.objects.filter(forum__name=forum_name)
            for thread in main_topics:
                last_message_by_time = list()
                comments = thread.thread_posts.all().order_by('datetime')          
                #replies = total_replies.filter( Q(reply_to_main_thread=thread.id) | Q(reply_to_comment=thread.id)  | Q(reply_to_older_reply=thread.id) ).order_by('datetime')
                replies = Reply.objects.filter(forum=thread.forum, thread_id=thread.id)

                threads_replies_amount[thread.title] = replies.count()
           

                if comments.count() != 0:
                    last_message_by_time.append(comments.last())
                if replies.count() != 0:
                    last_message_by_time.append(replies.last())

                last_message_by_time = sorted(last_message_by_time, key = attrgetter('datetime'), reverse=True)
                
                if len(last_message_by_time) != 0:
                    last_messages[thread.title] = last_message_by_time[0]
                else:
                    last_messages[thread.title] = "None"

            return (last_messages, threads_replies_amount)
    
    def get_context_data(self, **kwargs):
        context = super(ForumPostsListView, self).get_context_data(**kwargs)
        forum_name = self.kwargs['pk']
        main_topics = MainTopic.objects.filter(forum__name=forum_name)
        messages_details = self.get_last_message(forum_name, main_topics)
        context = dict(forum_name=forum_name, main_topics=main_topics, messages_details=messages_details[0], \
                       replies_amount=messages_details[1])

        return context

class ForumPostDetailView(DetailView):
    model = MainTopic
    template_name = 'forum/post_detail.html'


    def get_context_data(self, **kwargs):

        context = super(ForumPostDetailView, self).get_context_data(**kwargs)
        thread_pk = self.kwargs['pk']
        thread = MainTopic.objects.filter(id=thread_pk).first()
        comments = thread.thread_posts.all().order_by('datetime')          
        
        replies = Reply.objects.all().filter(forum=thread.forum, thread_id=thread.id)
        
        comments = list(comments.all())
        replies = list(replies.all())
        messages_thread = sorted(comments + replies, key = attrgetter('datetime') )

        context['forum_name'] = thread.forum
        context['post'] = thread
        context['messages_thread'] = messages_thread
        

        return context

    def get_absolute_url(self):
        return reverse_lazy('', kwargs={'pk': self.pk})