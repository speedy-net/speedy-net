from friendship.models import Friend
from rules import predicate, add_perm, is_authenticated
from django.conf import settings as django_settings

from speedy.core.accounts.base_rules import is_self
from speedy.core.blocks.rules import there_is_block


@predicate
def friendship_request_sent(user, other_user):
    return other_user.id in [fr.to_user_id for fr in Friend.objects.sent_requests(user=user)]


@predicate
def friendship_request_received(user, other_user):
    return user.id in [fr.to_user_id for fr in Friend.objects.sent_requests(user=other_user)]


@predicate
def is_friend(user, other_user):
    return Friend.objects.are_friends(user1=user, user2=other_user)


@predicate
def view_friend_list(user, other_user):
    # User can view other user's friends only on Speedy Net.
    # Otherwise (on Speedy Match), user can only view their own friends.
    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
        return True
    else:
        return (is_self(user=user, other_user=other_user))


are_friends = is_friend


add_perm('friends.request', is_authenticated & ~is_self & ~friendship_request_sent & ~is_friend & ~there_is_block)
add_perm('friends.cancel_request', is_authenticated & friendship_request_sent)
add_perm('friends.view_requests', is_self)
add_perm('friends.view_friend_list', view_friend_list)
add_perm('friends.remove', is_authenticated & is_friend)


