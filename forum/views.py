from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator

from django.contrib import messages
from django.db.models import Q
from django import forms as django_forms

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
                
                last_message_by_time = [ main_topics.last() ]
                comments = Comment.objects.filter(forum__name=forum.name).order_by('datetime')
                replies = Reply.objects.filter(forum__name=forum.name).order_by('datetime')
                number_of_messages = main_topics.count() + comments.count() + replies.count()

                if comments.count() != 0:
                    last_message_by_time.append(comments.last())
                if replies.count() != 0:
                    last_message_by_time.append(replies.last())

                last_message = sorted(last_message_by_time, key = attrgetter('datetime'), reverse=True)
                forum_details[forum.name] = (main_topics.count(), number_of_messages, last_message[0])
                
            return forum_details

    def get_context_data(self, **kwargs):
        context = super(ForumListView, self).get_context_data(**kwargs)

        forum_category = ForumCategory.objects.all()
        forums_list = Forum.objects.all()
        forum_details= self.get_forums_details(forums_list)

        context=dict(forum_category=forum_category, forum_details=forum_details)
        return context

class ForumPostsListView(ListView):
    model = MainTopic
    template_name = 'forum/forum.html'

    def get_last_message(self, forum_name, main_topics)->tuple:
        last_messages = dict()
        threads_posts_amount = dict()

        if main_topics.count() == 0:
            return "None"
        else:
            for thread in main_topics:
                last_message_by_time = list()
                comments = Comment.objects.filter(forum=thread.forum, thread_id=thread.id)
                replies = Reply.objects.filter(forum=thread.forum, thread_id=thread.id)

                threads_posts_amount[thread.title] = replies.count() + comments.count()

                if comments.count() != 0:
                    last_message_by_time.append(comments.last())
                if replies.count() != 0:
                    last_message_by_time.append(replies.last())

                last_message_by_time = sorted(last_message_by_time, key = attrgetter('datetime'), reverse=True)
                
                if len(last_message_by_time) != 0:
                    last_messages[thread.title] = last_message_by_time[0]
                else:
                    last_messages[thread.title] = "None"
                
            return (last_messages, threads_posts_amount)

    def get_context_data(self, **kwargs):
        context = super(ForumPostsListView, self).get_context_data(**kwargs)
        
        forum_name = self.kwargs['pk']
        pinned_messages = MainTopic.objects.filter(forum__name=forum_name, announcement='pinned')
        main_topics = MainTopic.objects.filter(forum__name=forum_name, announcement='normal')
        messages_details = self.get_last_message(forum_name, main_topics)

        paginator = Paginator(main_topics, 10) 
        page = self.request.GET.get('page')
        main_topics = paginator.get_page(page)

        context = dict(forum_name=forum_name, main_topics=main_topics, pinned_messages=pinned_messages, \
                       messages_details=messages_details[0], threads_posts_amount=messages_details[1])

        return context

class ForumPostDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'forum/post_detail.html'

    def get_context_data(self, **kwargs):

        context = super(ForumPostDetailView, self).get_context_data(**kwargs)
        thread_pk = self.kwargs['pk']
        thread = MainTopic.objects.filter(id=thread_pk).first()  
        comments = Comment.objects.all().filter(forum=thread.forum, thread_id=thread.id)
        replies = Reply.objects.all().filter(forum=thread.forum, thread_id=thread.id)
        
        comments = list(comments.all())
        replies = list(replies.all())
        messages_thread = sorted(comments + replies, key = attrgetter('datetime') )

        paginator = Paginator(messages_thread, 10) 
        page = self.request.GET.get('page')
        posts_list = paginator.object_list
    
        for post in posts_list:
           post.page_number = page

        paginator.object_list = posts_list

        messages_thread = paginator.get_page(page)
        context = dict(forum_name=thread.forum, post=thread, messages_thread=messages_thread)

        return context

    def get_absolute_url(self):
        return reverse_lazy('', kwargs={'pk': self.pk})

class ForumPostCreateView(LoginRequiredMixin, TemplateView):
    fields = ['title', 'message_body']

    def get(self, request, *args, **kwargs):

        new_post_form = NewPostForm()
        string_path = self.request.get_full_path()
        
        if string_path.find('reply') != -1:
            new_post_form.reply = True
            new_post_form.reply_to_main_thread  = MainTopic.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first()
            new_post_form.reply_to_comment  = Comment.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id'], thread_id=kwargs['pk']).first()
            new_post_form.reply_to_older_reply = Reply.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id'], thread_id=kwargs['pk']).first()

        user = request.user
        current_forum = Forum.objects.filter(name=kwargs['forum']).first()

        # Comment or Reply
        if 'pk' in kwargs: 
            new_post_form.fields['title'].widget = django_forms.HiddenInput()
            new_post_form.fields['title'].required = False
            new_post_form.fields['announcement'].widget = django_forms.HiddenInput()
            new_post_form.fields['announcement'].required = False
            new_post_form.fields['closed'].widget = django_forms.HiddenInput()
            new_post_form.fields['closed'].required = False
        # MainTopic for registered user
        elif user.is_superuser == False and user.is_staff == False and user not in current_forum.moderator.all():
            new_post_form.fields['closed'].widget = django_forms.HiddenInput()
            new_post_form.fields['closed'].required = False
            new_post_form.fields['announcement'].widget = django_forms.HiddenInput()
            new_post_form.fields['announcement'].required = False

        return render(request, 'forum/new_post.html', {'new_post_form': new_post_form, 'kwargs':kwargs})
    
    def post(self, request, *args, **kwargs):

        new_post_form = NewPostForm(request.POST)

        if 'pk' in kwargs:
            new_post_form.fields['title'].widget = django_forms.HiddenInput()
            new_post_form.fields['title'].required = False

        if new_post_form.is_valid():
            
            string_path = self.request.get_full_path()

            new_post = None
            result_redirect = None
            if string_path.find('reply') != -1:
                new_post = Reply.objects.create(author=self.request.user, datetime=date_time.now(), \
                           message_body=request.POST['message_body'], forum=Forum.objects.all().filter(name=kwargs['forum']).first(), \
                           thread_id=MainTopic.objects.all().filter(forum__name=kwargs['forum'], id=kwargs['pk']).first(), \
                           reply_to_main_thread=MainTopic.objects.all().filter(forum__name=kwargs['forum'], id=kwargs['id']).first(), \
                           reply_to_comment=Comment.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first(), \
                           reply_to_older_reply=Reply.objects.all().filter(forum__name=kwargs['forum'],id=kwargs['id']).first())
                result_redirect = redirect('forum:post-detail', kwargs['forum'], kwargs['pk'])

            elif string_path.find('comment') != -1:
                new_post = Comment.objects.create(author=self.request.user, datetime=date_time.now(), \
                           message_body=request.POST['message_body'], forum=Forum.objects.all().filter(name=kwargs['forum']).first(), \
                           thread_id=MainTopic.objects.all().filter(forum__name=kwargs['forum'], id=kwargs['pk']).first())
                result_redirect = redirect('forum:post-detail', kwargs['forum'], kwargs['pk']) 

            else:
                is_closed = False
                if 'closed' in request.POST:
                    is_closed = True
               
                new_post = MainTopic.objects.create(author=self.request.user, datetime=date_time.now(),announcement=request.POST['announcement'], \
                                                    closed=is_closed, title=request.POST['title'], message_body=request.POST['message_body'], \
                                                    forum=Forum.objects.all().filter(name=kwargs['forum']).first())
                result_redirect = redirect('forum:forum-board', kwargs['forum'])

            new_post.save()

            user = self.request.user
            user.profile.posts_counter += 1
            user.profile.save()

            messages.success(request, "Your Post Has Been Published!")
            return result_redirect

        else:
            print("error: ", new_post_form.errors)
            new_post_form = NewPostForm(request.POST)

            return render(request, 'forum/new_post.html', {'new_post_form': new_post_form})

class ForumPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'forum/update_post.html'
    fields = ['title', 'message_body']
   
    def test_func(self, *args, **kwargs):

        current_forum = Forum.objects.filter(name=self.kwargs['forum']).first()
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser or self.request.user.is_staff or self.request.user in current_forum.moderator.all():
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(ForumPostUpdateView, self).get_context_data(**kwargs)
        current_object = self.get_object()

        request = kwargs        
        request['message_body'] = current_object.message_body
        
        form = NewPostForm(request)
        if current_object.__class__.__name__ == "MainTopic":
            request['title'] = current_object.title
            request['announcement'] = current_object.announcement
            request['closed'] = current_object.closed
        else:
            form.fields['title'].widget = django_forms.HiddenInput()
            form.fields['announcement'].widget = django_forms.HiddenInput()
            form.fields['closed'].widget = django_forms.HiddenInput()
            
        context=dict(form=form, object=current_object)
        return context

    def get_object(self, queryset=None):
        
        string_path = self.request.get_full_path()
        
        if string_path.find('reply') != -1:
            current_object = Reply.objects.get(forum__name=self.kwargs['forum'], id=self.kwargs['id'])
            current_object.main_topic = self.kwargs['pk']
        elif string_path.find('comment') != -1:
            current_object = Comment.objects.get(forum__name=self.kwargs['forum'], id=self.kwargs['id'])
            current_object.main_topic = self.kwargs['pk']
        else:
            current_object = MainTopic.objects.get(forum__name=self.kwargs['forum'], id=self.kwargs['pk'])
        
        return current_object

    def post(self, request, *args, **kwargs):
        post_to_update = self.get_object()
                
        form = NewPostForm(self.request.POST)

        if post_to_update.__class__.__name__ != 'MainTopic':
            form.fields['title'].required = False
            form.fields['title'].widget = django_forms.HiddenInput()
            form.fields['announcement'].required = False
            form.fields['announcement'].widget = django_forms.HiddenInput()
            form.fields['closed'].required = False
            form.fields['closed'].widget = django_forms.HiddenInput()
        else:
            post_to_update.title = f"{request.POST['title']}"
            post_to_update.announcement = request.POST['announcement']

            if 'closed' in request.POST:
                post_to_update.closed = True
            else:
                post_to_update.closed = False
        
        operation_result = None
        if form.is_valid():
            post_to_update.message_body = request.POST['message_body']
            post_to_update.save()           

            operation_result = redirect('forum:post-detail', kwargs['forum'], kwargs['pk'])  
        
        else:
            print("error: ", form.errors)
            operation_result = render(request, 'forum/update_post.html', {'form': form})

        return operation_result

class ForumPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'forum/post_confirm_delete.html'
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(ForumPostDeleteView, self).get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

    def get_object(self, queryset=None):
        current_object = Chat.objects.filter(participants__in=self.request.user)

        return current_object

    def post(self, request, *args, **kwargs):
       
        messages.success(request, "Your Post Has Been Deleted")
        post_to_delete = self.get_object()
        class_name = post_to_delete.__class__.__name__
        
        result = None
        if class_name is 'MainTopic':
            result = redirect('forum:forum-board', kwargs['forum'])
        else:
            result = redirect('forum:post-detail', kwargs['forum'], kwargs['pk'])

        user = post_to_delete.author
        user.profile.posts_counter -= 1
        user.profile.save()
        
        post_to_delete.delete()

        return result

class SearchResultsView(LoginRequiredMixin, DetailView):
    template_name = 'search_results.html'

    def get(self, request, *args, **kwargs):
        search_results = self.get_queryset()

        return render(request, 'forum/search_results.html', {'search_results': search_results})

    def get_queryset(self):
        query = self.request.GET.get('q')

        maintopics_list = MainTopic.objects.filter( Q(title__icontains=query) | Q(message_body__icontains=query) )
        comments_list = Comment.objects.filter(message_body__icontains=query)
        replies_list = Reply.objects.filter(message_body__icontains=query)
        users = User.objects.filter(username__icontains=query)

        maintopics_list = list(maintopics_list.all())
        comments_list = list(comments_list.all())
        replies_list = list(replies_list.all())
        object_list = list(users.all())

        messages = sorted(maintopics_list + comments_list + replies_list, key = attrgetter('datetime') )
        object_list += messages

        return object_list
