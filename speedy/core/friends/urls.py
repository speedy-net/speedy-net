from django.conf.urls import url

from . import views

app_name = 'speedy.core.friends'
urlpatterns = [
    url(regex=r'^$', view=views.UserFriendListView.as_view(), name='list'),
    url(regex=r'^received-requests/$', view=views.ReceivedFriendshipRequestsListView.as_view(), name='received_requests'),
    url(regex=r'^sent-requests/$', view=views.SentFriendshipRequestsListView.as_view(), name='sent_requests'),
    url(regex=r'^request/$', view=views.FriendshipRequestView.as_view(), name='request'),
    url(regex=r'^request/cancel/$', view=views.CancelFriendshipRequestView.as_view(), name='cancel_request'),
    url(regex=r'^request/accept/(?P<friendship_request_id>\d+)/$', view=views.AcceptFriendshipRequestView.as_view(), name='accept_request'),
    url(regex=r'^request/reject/(?P<friendship_request_id>\d+)/$', view=views.RejectFriendshipRequestView.as_view(), name='reject_request'),
    url(regex=r'^remove/$', view=views.RemoveFriendView.as_view(), name='remove'),
]


