from rules import predicate, add_perm, is_authenticated

from speedy.core.accounts.base_rules import is_self
from speedy.core.blocks.rules import there_is_block
from speedy.core.accounts.models import User
from .models import UserLike


@predicate
def you_like_user(user, other_user):
    """
    Checks whether the given user already likes the other user.

    :param user: The user who may like the other user.
    :type user: speedy.core.accounts.models.User
    :param other_user: The other user.
    :type other_user: speedy.core.accounts.models.User
    :return: True if a like from user to other_user exists, False otherwise.
    :rtype: bool
    """
    return UserLike.objects.filter(from_user=user, to_user=other_user).exists()


@predicate
def user_likes_you(user, other_user):
    """
    Checks whether the other user already likes the given user.

    :param user: The user who may be liked.
    :type user: speedy.core.accounts.models.User
    :param other_user: The other user who may like the given user.
    :type other_user: speedy.core.accounts.models.User
    :return: True if a like from other_user to user exists, False otherwise.
    :rtype: bool
    """
    return UserLike.objects.filter(from_user=other_user, to_user=user).exists()


@predicate
def both_are_users(user, other_user):
    """
    Checks whether both arguments are User instances.

    :param user: The first entity to check.
    :param other_user: The second entity to check.
    :return: True if both are User instances, False otherwise.
    :rtype: bool
    """
    return ((isinstance(user, User)) and (isinstance(other_user, User)))


add_perm(name='likes.like', pred=is_authenticated & ~is_self & ~there_is_block & ~you_like_user & both_are_users)
add_perm(name='likes.unlike', pred=is_authenticated & ~is_self & ~there_is_block & you_like_user & both_are_users)
add_perm(name='likes.view_likes', pred=is_authenticated & is_self)


