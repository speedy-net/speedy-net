from rules import predicate, add_perm, is_authenticated

from .models import Block


@predicate
def is_self(user, other):
    return user == other


@predicate
def has_blocked(user, other):
    return Block.objects.has_blocked(blocker=user, blockee=other)


@predicate
def is_blocked(user, other):
    return Block.objects.has_blocked(blocker=other, blockee=user)


add_perm('blocks.block', is_authenticated & ~is_self & ~has_blocked)
add_perm('blocks.unblock', is_authenticated & ~is_self & has_blocked)
