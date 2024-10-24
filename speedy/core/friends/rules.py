from friendship.models import Friend, FriendshipRequest
from rules import predicate, add_perm, is_authenticated
from django.conf import settings as django_settings

from speedy.core.accounts.base_rules import is_self
from speedy.core.blocks.rules import there_is_block


@predicate
def friendship_request_sent(user, other_user):
    return FriendshipRequest.objects.filter(from_user=user, to_user=other_user).exists()


@predicate
def friendship_request_received(user, other_user):
    return FriendshipRequest.objects.filter(from_user=other_user, to_user=user).exists()


@predicate
def are_friends(user, other_user):
    return Friend.objects.are_friends(user1=user, user2=other_user)


@predicate
def view_friend_list(user, other_user):
    # User can view other user's friends only on Speedy Net.
    # Otherwise (on Speedy Match), user can only view their own friends.
    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
        return True
    else:
        return (is_self(user=user, other_user=other_user))


add_perm('friends.request', is_authenticated & ~is_self & ~friendship_request_sent & ~are_friends & ~there_is_block)
add_perm('friends.cancel_request', is_authenticated & friendship_request_sent)
add_perm('friends.view_requests', is_self)
add_perm('friends.view_friend_list', view_friend_list)
add_perm('friends.remove', is_authenticated & are_friends)


