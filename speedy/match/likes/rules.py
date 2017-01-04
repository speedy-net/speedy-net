from rules import predicate, add_perm, is_authenticated

from speedy.net.accounts.models import User
from speedy.net.blocks.rules import is_blocked
from .models import EntityLike


@predicate
def is_self(user, other):
    return user == other


@predicate
def already_likes(user, other):
    return EntityLike.objects.filter(from_user=user, to_user=other).exists()

@predicate
def both_are_users(user, other):
    return isinstance(user, User) and isinstance(other, User)


add_perm('likes.like', is_authenticated & ~is_self & ~is_blocked & ~already_likes & both_are_users)
add_perm('likes.unlike', is_authenticated & ~is_self & already_likes & both_are_users)
add_perm('likes.view_likes', is_authenticated & is_self)
