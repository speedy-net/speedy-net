from django.urls import path

from . import views

app_name = 'speedy.core.messages'
urlpatterns = [
    path(route='', view=views.ChatListView.as_view(), name='list'),
    path(route='<speedy_slug:chat_slug>/', view=views.ChatDetailView.as_view(), name='chat'),
    path(route='<speedy_slug:chat_slug>/poll/', view=views.ChatPollMessagesView.as_view(), name='chat_poll'),
    path(route='<speedy_slug:chat_slug>/send/', view=views.SendMessageToChatView.as_view(), name='chat_send'),
    path(route='<speedy_slug:chat_slug>/mark-read/', view=views.MarkChatAsReadView.as_view(), name='mark_read'),
]


