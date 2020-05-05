from django.urls import re_path

from . import views

app_name = 'speedy.core.messages'
urlpatterns = [
    re_path(route=r'^$', view=views.ChatListView.as_view(), name='list'),
    re_path(route=r'^(?P<chat_slug>[-._\w]+)/$', view=views.ChatDetailView.as_view(), name='chat'),
    re_path(route=r'^(?P<chat_slug>[-\w]+)/poll/$', view=views.ChatPollMessagesView.as_view(), name='chat_poll'),
    re_path(route=r'^(?P<chat_slug>[-\w]+)/send/$', view=views.SendMessageToChatView.as_view(), name='chat_send'),
    re_path(route=r'^(?P<chat_slug>[-\w]+)/mark-read/$', view=views.MarkChatAsReadView.as_view(), name='mark_read'),
]


