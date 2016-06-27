from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.UserFriendListView.as_view(), name='list'),
    url(r'^request/$', views.FriendRequestView.as_view(), name='request'),
]
