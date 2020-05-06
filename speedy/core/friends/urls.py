from django.urls import path

from . import views

app_name = 'speedy.core.friends'
urlpatterns = [
    path(route='', view=views.UserFriendListView.as_view(), name='list'),
    path(route='received-requests/', view=views.ReceivedFriendshipRequestsListView.as_view(), name='received_requests'),
    path(route='sent-requests/', view=views.SentFriendshipRequestsListView.as_view(), name='sent_requests'),
    path(route='request/', view=views.FriendshipRequestView.as_view(), name='request'),
    path(route='request/cancel/', view=views.CancelFriendshipRequestView.as_view(), name='cancel_request'),
    path(route='request/accept/<digits:friendship_request_id>/', view=views.AcceptFriendshipRequestView.as_view(), name='accept_request'),
    path(route='request/reject/<digits:friendship_request_id>/', view=views.RejectFriendshipRequestView.as_view(), name='reject_request'),
    path(route='remove/', view=views.RemoveFriendView.as_view(), name='remove'),
]


