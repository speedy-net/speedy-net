from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.UserFriendListView.as_view(), name='list'),
    url(r'^request/$', views.FriendRequestView.as_view(), name='request'),
    url(r'^request/accept/(?P<friendship_request_id>\d+)/$', views.AcceptFriendRequestView.as_view(),
        name='accept_request'),
    url(r'^request/reject/(?P<friendship_request_id>\d+)/$', views.RejectFriendRequestView.as_view(),
        name='reject_request'),
]
