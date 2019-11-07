from django.urls import path
# from django.contrib.auth import views as auth_views
# from forum import views as user_views
# from .views import ForumListView, ForumPostsListView, ForumPostDetailView, ForumPostCreateView, ForumPostUpdateView, ForumPostDeleteView, \
#                     SearchResultsView
from .views import ChatWindowListView

app_name = 'chat'

urlpatterns = [
    path('private-messages/<user>', ChatWindowListView.as_view(), name='chat-window'),
    # path('<str:pk>/', ForumPostsListView.as_view(), name='forums-list'),
    # path('<forum>/', ForumPostDetailView.as_view(), name='forum-board'),#Backwards
    # path('<forum>/post/new/', ForumPostCreateView.as_view(), name='new-post'),
    # path('<forum>/post/<str:pk>/comment/', ForumPostCreateView.as_view(), name='new-comment'),
    # path('<forum>/post/<str:pk>/<str:id>/reply/', ForumPostCreateView.as_view(), name='new-reply'),
    # path('<forum>/post/<str:pk>/', ForumPostDetailView.as_view(), name='post-detail'),
    # path('<forum>/post/<str:pk>/update/', ForumPostUpdateView.as_view(), name='post-update'),
    # path('<forum>/post/<str:pk>/<str:id>/comment/update/', ForumPostUpdateView.as_view(), name='comment-update'),
    # path('<forum>/post/<str:pk>/<str:id>/reply/update/', ForumPostUpdateView.as_view(), name='reply-update'),
    # path('<forum>/post/<str:pk>/delete/', ForumPostDeleteView.as_view(), name='post-delete'),
    # path('<forum>/post/<str:pk>/<str:id>/comment/delete/', ForumPostDeleteView.as_view(), name='comment-delete'),
    # path('<forum>/post/<str:pk>/<str:id>/reply/delete/', ForumPostDeleteView.as_view(), name='reply-delete'),
]