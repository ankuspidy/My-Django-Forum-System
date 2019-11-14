from django.urls import path
from django.conf.urls import url
from .views import ChatWindowListView, ChatWindowDeleteView

app_name = 'chat'

urlpatterns = [
    path('private-messages/<user>', ChatWindowListView.as_view(), name='chat-window'),
    path('private-messages/<user>/delete', ChatWindowDeleteView.as_view(), name='chat-window-delete'),
]