from rules import predicate, add_perm, is_authenticated

from speedy.core.accounts.base_rules import is_self
from .models import Block


@predicate
def has_blocked(user, other_user):
    return Block.objects.has_blocked(blocker=user, blocked=other_user)


@predicate
def is_blocked(user, other_user):
    return Block.objects.has_blocked(blocker=other_user, blocked=user)


@predicate
def there_is_block(user, other_user):
    return Block.objects.there_is_block(entity_1=user, entity_2=other_user)


add_perm('blocks.block', is_authenticated & ~is_self & ~has_blocked)
add_perm('blocks.unblock', is_authenticated & ~is_self & has_blocked)


