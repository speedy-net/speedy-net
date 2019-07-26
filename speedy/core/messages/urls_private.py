from django.conf.urls import url

from . import views

app_name = 'speedy.core.messages'
urlpatterns = [
    url(regex=r'^$', view=views.ChatListView.as_view(), name='list'),
    url(regex=r'^(?P<chat_slug>[-._\w]+)/$', view=views.ChatDetailView.as_view(), name='chat'),
    url(regex=r'^(?P<chat_slug>[-\w]+)/poll/$', view=views.ChatPollMessagesView.as_view(), name='chat_poll'),
    url(regex=r'^(?P<chat_slug>[-\w]+)/send/$', view=views.SendMessageToChatView.as_view(), name='chat_send'),
    url(regex=r'^(?P<chat_slug>[-\w]+)/mark-read/$', view=views.MarkChatAsReadView.as_view(), name='mark_read'),
]


