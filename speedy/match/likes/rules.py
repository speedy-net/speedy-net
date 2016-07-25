from rules import predicate, add_perm, is_authenticated

from speedy.net.blocks.rules import is_blocked
from .models import EntityLike


@predicate
def is_self(user, other):
    return user == other


@predicate
def already_likes(user, other):
    return EntityLike.objects.filter(from_user=user, to_entity=other).exists()


add_perm('likes.like', is_authenticated & ~is_self & ~is_blocked & ~already_likes)
add_perm('likes.unlike', is_authenticated & ~is_self & already_likes)
add_perm('likes.view_likes', is_authenticated & is_self)
