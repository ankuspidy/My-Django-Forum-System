from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from django.contrib.auth import views as auth_views
from forum import views as user_views
from .views import ForumListView, ForumPostsListView, ForumPostDetailView, ForumNewPostCreateView, ForumNewCommentCreateView, \
                   ForumNewReplyCreateView, ForumPostUpdateView, ForumCommentUpdateView, ForumReplyUpdateView

app_name = 'forum'

urlpatterns = [
    path('', ForumListView.as_view(), name='home'),
    path('<str:pk>/', ForumPostsListView.as_view(), name='forums-list'),
    path('<forum>/', ForumPostDetailView.as_view(), name='forum-board'),#Backwards
    path('<forum>/post/new/', ForumNewPostCreateView.as_view(), name='new-post'),
    path('<forum>/post/<str:pk>/comment/', ForumNewCommentCreateView.as_view(), name='new-comment'),
    path('<forum>/post/<str:pk>/<str:id>/reply/', ForumNewReplyCreateView.as_view(), name='new-reply'),
    path('<forum>/post/<str:pk>/', ForumPostDetailView.as_view(), name='post-detail'),
    path('<forum>/post/<str:pk>/update/', ForumPostUpdateView.as_view(), name='post-update'),
    path('<forum>/post/<str:pk>/<str:id>/comment/update/', ForumCommentUpdateView.as_view(), name='comment-update'),
    path('<forum>/post/<str:pk>/<str:id>/reply/update/', ForumReplyUpdateView.as_view(), name='reply-update'),
    #path('<forum>/<str:str>/<str:pk>/delete/', ForumPostDeleteView.as_view(), name='post-delete'),

    
    


]