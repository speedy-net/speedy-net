from friendship.models import Friend
from rules import predicate, add_perm, is_authenticated


@predicate
def user_is_self(user, other):
    return user == other


@predicate
def friend_request_sent(user, other):
    return other in Friend.objects.sent_requests(user)


@predicate
def users_are_friends(user, other):
    return Friend.objects.are_friends(user, other)


add_perm('friends.request', is_authenticated & ~user_is_self & ~friend_request_sent & ~users_are_friends)
add_perm('friends.view_requests', user_is_self)
