from friendship.models import Friend, FriendshipRequest
from rules import predicate, add_perm, is_authenticated
from django.conf import settings as django_settings

from speedy.core.accounts.base_rules import is_self
from speedy.core.blocks.rules import there_is_block


@predicate
def friendship_request_sent(user, other_user):
    """
    Check whether ``user`` has sent a friendship request to ``other_user``.

    :param user: The user who may have sent the friendship request.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user who may have received the friendship request.
    :type other_user: speedy.core.accounts.models.User
    :return: ``True`` if ``user`` has sent a friendship request to ``other_user``, ``False`` otherwise.
    :rtype: bool
    """
    return FriendshipRequest.objects.filter(from_user=user, to_user=other_user).exists()


@predicate
def friendship_request_received(user, other_user):
    """
    Check whether ``user`` has received a friendship request from ``other_user``.

    :param user: The user who may have received the friendship request.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user who may have sent the friendship request.
    :type other_user: speedy.core.accounts.models.User
    :return: ``True`` if ``user`` has received a friendship request from ``other_user``, ``False`` otherwise.
    :rtype: bool
    """
    return FriendshipRequest.objects.filter(from_user=other_user, to_user=user).exists()


@predicate
def are_friends(user, other_user):
    """
    Check whether ``user`` and ``other_user`` are friends.

    :param user: The first user.
    :type user: speedy.core.accounts.models.User
    :param other_user: The second user.
    :type other_user: speedy.core.accounts.models.User
    :return: ``True`` if ``user`` and ``other_user`` are friends, ``False`` otherwise.
    :rtype: bool
    """
    return Friend.objects.are_friends(user1=user, user2=other_user)


@predicate
def view_friend_list(user, other_user):
    """
    Check whether ``user`` has permission to view ``other_user``'s friend list.

    User can view other user's friends only on Speedy Net.
    Otherwise (on Speedy Match), user can only view their own friends.

    :param user: The user requesting to view the friend list.
    :type user: speedy.core.accounts.models.User
    :param other_user: The user whose friend list is being requested.
    :type other_user: speedy.core.accounts.models.User
    :return: ``True`` if ``user`` has permission to view ``other_user``'s friend list, ``False`` otherwise.
    :rtype: bool
    """
    # User can view other user's friends only on Speedy Net.
    # Otherwise (on Speedy Match), user can only view their own friends.
    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
        return True
    else:
        return (is_self(user=user, other_user=other_user))


add_perm(name='friends.request', pred=is_authenticated & ~is_self & ~friendship_request_sent & ~are_friends & ~there_is_block)
add_perm(name='friends.cancel_request', pred=is_authenticated & friendship_request_sent)
add_perm(name='friends.view_requests', pred=is_self)
add_perm(name='friends.view_friend_list', pred=view_friend_list)
add_perm(name='friends.remove', pred=is_authenticated & are_friends)


