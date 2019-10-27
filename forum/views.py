from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

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
                    continue
                
                times = [ main_topics.last() ]
                comments = Comment.objects.filter(forum__name=forum.name).order_by('datetime')
                replies = Reply.objects.filter(forum__name=forum.name).order_by('datetime')
                number_of_messages = main_topics.count() + comments.count() + replies.count()

                if comments.count() != 0:
                    times.append(comments.last())
                if replies.count() != 0:
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

    def get_last_message(self, messages_list)->dict:
        last_messages = dict()

        if messages_list.count() == 0:
            return "None"
        else:
            for message in messages_list:

                last_message_by_time = list()
                comments = message.comments.all().order_by('datetime')
                replies = message.replies.all().order_by('datetime')

                if comments.count() != 0:
                    last_message_by_time.append(comments.last())
                if replies.count() != 0:
                    last_message_by_time.append(replies.last())

                last_message_by_time = sorted(last_message_by_time, key = attrgetter('datetime'), reverse=True)
                
                if len(last_message_by_time) != 0:
                    last_messages[message.title] = last_message_by_time[0]
                else:
                    last_messages[message.title] = "None"

                
            return last_messages
    
    def get_context_data(self, **kwargs):
        context = super(ForumPostsListView, self).get_context_data(**kwargs)
        forum_name = self.kwargs['pk']
        posts = MainTopic.objects.filter(forum__name=forum_name)
        messages_details = self.get_last_message(posts)
        context = dict(forum_name=forum_name, posts=posts, messages_details=messages_details)
        # context['forum_name'] = forum_name          
        # context['posts'] = posts

        return context

class ForumPostDetailView(DetailView):
    model = MainTopic
    template_name = 'forum/post_detail.html'


    def get_context_data(self, **kwargs):

        context = super(ForumPostDetailView, self).get_context_data(**kwargs)
        post_pk = self.kwargs['pk']
        post = MainTopic.objects.filter(id=post_pk).first()
        comments = list(post.comments.all())
        replies = list(post.replies.all())
        messages_thread = sorted(comments + replies, key = attrgetter('datetime') )
        
        #messages_thread = comments.union(replies)#.orderby('date_time')
        context['forum_name'] = post.forum
        context['post'] = post
        context['messages_thread'] = messages_thread
        

        return context

    def get_absolute_url(self):
        print(self)
        print(dir(self.request))
        print(self.args)
        return reverse_lazy('', kwargs={'pk': self.pk})