from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Forum, ForumCategory, MainTopic, Comment, Reply
from .forms import NewPostForm, NewCommentForm, NewReplyForm

from datetime import datetime as date_time
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
            for thread in main_topics:
                last_message_by_time = list()
                comments = thread.thread_posts.all().order_by('datetime')          
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

        context = dict(forum_name=thread.forum, post=thread, messages_thread=messages_thread)

        return context

    def get_absolute_url(self):
        return reverse_lazy('', kwargs={'pk': self.pk})

class ForumNewPostCreateView(LoginRequiredMixin, CreateView):
    model = MainTopic
    fields = ['title', 'message_body']

    def get(self, request, *args, **kwargs):
        new_post_form = NewPostForm()

        return render(request, 'forum/new_post.html', {'new_post_form': new_post_form})
    
    def post(self, request, *args, **kwargs):

        new_post_form = NewPostForm(request.POST)

        if new_post_form.is_valid():
            
            new_post_form.instance.author = self.request.user
            new_post_form.instance.datetime = new_post_form.cleaned_data.get('datetime')
            new_post_form.instance.forum =  Forum.objects.all().filter(name=kwargs['forum']).first()
            new_post_form.save()

            messages.success(request, "Your Post Has Been Published!")
            return redirect('forum:forum-board', kwargs['forum'])

        else:
            print("error: ", new_post_form.errors)
            new_post_form = NewPostForm(request.POST)

            return render(request, 'forum/new_post.html', {'new_post_form': new_post_form})

class ForumNewCommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['message_body']

    def get(self, request, *args, **kwargs):
        new_comment_form = NewCommentForm()

        return render(request, 'forum/new_comment.html', {'new_comment_form': new_comment_form})
    
    def post(self, request, *args, **kwargs):

        new_comment_form = NewCommentForm(request.POST)

        if new_comment_form.is_valid():
            
            main_topic =  MainTopic.objects.all().filter(forum__name=kwargs['forum'], id=kwargs['pk']).first()
            comment = new_comment_form.instance
            comment.author = self.request.user
            comment.datetime = new_comment_form.cleaned_data.get('datetime')
            comment.forum =  Forum.objects.all().filter(name=kwargs['forum']).first()          
            
            comment.save()
            main_topic.thread_posts.add(comment.pk)
            
            new_comment_form.save()

            return redirect('forum:forum-board', kwargs['forum'])

        else:
            print("error: ", new_comment_form.errors)
            new_comment_form = NewCommentForm(request.POST)

            return render(request, 'forum/new_comment.html', {'new_comment_form': new_comment_form})

class ForumNewReplyCreateView(LoginRequiredMixin, CreateView):
    model = Reply
    fields = ['message_body']

    def get(self, request, *args, **kwargs):
        new_reply_form = NewReplyForm()

        return render(request, 'forum/new_reply.html', {'new_reply_form': new_reply_form})
    
    def post(self, request, *args, **kwargs):

        new_reply_form = NewReplyForm(request.POST)

        if new_reply_form.is_valid():

            main_topic =  MainTopic.objects.all().filter(forum__name=kwargs['forum'], id=kwargs['pk']).first()

            # reply_to_main_topic = MainTopic.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first()
            # comment_to_reply = Comment.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first()
            # reply_to_reply = Reply.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first()

            # print(reply_to_main_topic)
            # print(reply_to_reply)
            # print(comment_to_reply)
            # thread_id = models.ForeignKey(MainTopic, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
            # reply_to_main_thread = models.ForeignKey(MainTopic, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
            # reply_to_comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.CASCADE, related_name='+')
            # reply_to_older_reply = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)#    
            
            
            reply = new_reply_form.instance

            reply.thread_id = main_topic
            reply.reply_to_main_thread  = MainTopic.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first()
            reply.reply_to_comment  = Comment.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first()
            reply.reply_to_older_reply = Reply.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first()


            reply.author = self.request.user
            reply.datetime = new_reply_form.cleaned_data.get('datetime')
            reply.forum =  Forum.objects.all().filter(name=kwargs['forum']).first()      
  
            
            reply.save()
            #main_topic.thread_posts.add(comment.pk)
            
            new_reply_form.save()

            return redirect('forum:forum-board', kwargs['forum'])

        else:
            print("error: ", new_reply_form.errors)
            new_reply_form = NewReplyForm(request.POST)
            
            return render(request, 'forum/new_reply.html', {'new_reply_form': new_reply_form})

