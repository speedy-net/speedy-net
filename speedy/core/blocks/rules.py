"""
Permission rules for the blocks app of Speedy Core, which define predicates such as has_blocked, is_blocked and there_is_block.
"""
from rules import predicate, add_perm, is_authenticated

from speedy.core.accounts.base_rules import is_self
from .models import Block


@predicate
def has_blocked(user, other_user):
    """
    Rule predicate checking whether user has blocked other_user.

    :param user: The entity that may have blocked other_user.
    :type user: speedy.core.accounts.models.Entity
    :param other_user: The entity that may be blocked.
    :type other_user: speedy.core.accounts.models.Entity
    :return: True if user has blocked other_user, False otherwise.
    :rtype: bool
    """
    return Block.objects.has_blocked(blocker=user, blocked=other_user)


@predicate
def is_blocked(user, other_user):
    """
    Rule predicate checking whether user is blocked by other_user.

    :param user: The entity that may be blocked.
    :type user: speedy.core.accounts.models.Entity
    :param other_user: The entity that may have blocked user.
    :type other_user: speedy.core.accounts.models.Entity
    :return: True if other_user has blocked user, False otherwise.
    :rtype: bool
    """
    return Block.objects.has_blocked(blocker=other_user, blocked=user)


@predicate
def there_is_block(user, other_user):
    """
    Rule predicate checking whether there is a block between user and other_user, in either direction.

    :param user: The first entity.
    :type user: speedy.core.accounts.models.Entity
    :param other_user: The second entity.
    :type other_user: speedy.core.accounts.models.Entity
    :return: True if either entity has blocked the other, False otherwise.
    :rtype: bool
    """
    return Block.objects.there_is_block(entity_1=user, entity_2=other_user)


add_perm(name='blocks.block', pred=is_authenticated & ~is_self & ~has_blocked)
add_perm(name='blocks.unblock', pred=is_authenticated & ~is_self & has_blocked)


