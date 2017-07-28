from friendship.models import Friend
from rules import predicate, add_perm, is_authenticated

from speedy.core.blocks.rules import there_is_block


@predicate
def is_self(user, other):
    return user == other


@predicate
def friend_request_sent(user, other):
    return other.id in [fr.to_user_id for fr in Friend.objects.sent_requests(user=user)]


@predicate
def is_friend(user, other):
    return Friend.objects.are_friends(user1=user, user2=other)


add_perm('friends.request', is_authenticated & ~is_self & ~friend_request_sent & ~is_friend & ~there_is_block)
add_perm('friends.cancel_request', is_authenticated & friend_request_sent)
add_perm('friends.view_requests', is_self)
add_perm('friends.remove', is_authenticated & is_friend)

