from django.conf.urls import url

from . import views

app_name = 'speedy.core.friends'
urlpatterns = [
    url(r'^$', views.UserFriendListView.as_view(), name='list'),
    url(r'^received-requests/$', views.ReceivedFriendshipRequestsListView.as_view(), name='received_requests'),
    url(r'^sent-requests/$', views.SentFriendshipRequestsListView.as_view(), name='sent_requests'),
    url(r'^request/$', views.FriendRequestView.as_view(), name='request'),
    url(r'^request/cancel/$', views.CancelFriendRequestView.as_view(), name='cancel_request'),
    url(r'^request/accept/(?P<friendship_request_id>\d+)/$', views.AcceptFriendRequestView.as_view(), name='accept_request'),
    url(r'^request/reject/(?P<friendship_request_id>\d+)/$', views.RejectFriendRequestView.as_view(), name='reject_request'),
    url(r'^remove/$', views.RemoveFriendView.as_view(), name='remove'),
]


