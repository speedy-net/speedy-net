from django.urls import re_path

from . import views

app_name = 'speedy.core.friends'
urlpatterns = [
    re_path(route=r'^$', view=views.UserFriendListView.as_view(), name='list'),
    re_path(route=r'^received-requests/$', view=views.ReceivedFriendshipRequestsListView.as_view(), name='received_requests'),
    re_path(route=r'^sent-requests/$', view=views.SentFriendshipRequestsListView.as_view(), name='sent_requests'),
    re_path(route=r'^request/$', view=views.FriendshipRequestView.as_view(), name='request'),
    re_path(route=r'^request/cancel/$', view=views.CancelFriendshipRequestView.as_view(), name='cancel_request'),
    re_path(route=r'^request/accept/(?P<friendship_request_id>\d+)/$', view=views.AcceptFriendshipRequestView.as_view(), name='accept_request'),
    re_path(route=r'^request/reject/(?P<friendship_request_id>\d+)/$', view=views.RejectFriendshipRequestView.as_view(), name='reject_request'),
    re_path(route=r'^remove/$', view=views.RemoveFriendView.as_view(), name='remove'),
]


