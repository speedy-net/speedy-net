from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ChatListView.as_view(), name='list'),
    url(r'^(?P<chat_pk>[-\w]{36})/$', views.ChatDetailView.as_view(), name='chat'),
    url(r'^(?P<chat_pk>[-\w]{36})/send/$', views.SendMessageToChatView.as_view(), name='chat_send'),
    url(r'^compose/$', views.SendMessageToUserView.as_view(), name='user_send'),
]
