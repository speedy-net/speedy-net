from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ChatListView.as_view(), name='list'),
    url(r'^(?P<chat_slug>[-._\w]+)/$', views.ChatDetailView.as_view(), name='chat'),
    url(r'^(?P<chat_slug>[-\w]+)/poll/$', views.ChatPollMessagesView.as_view(), name='chat_poll'),
    url(r'^(?P<chat_slug>[-\w]+)/send/$', views.SendMessageToChatView.as_view(), name='chat_send'),
    url(r'^(?P<chat_slug>[-\w]+)/mark-read/$', views.MarkChatAsReadView.as_view(), name='mark_read'),
]
