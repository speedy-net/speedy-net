from django.db.models import Q

from rules import predicate, add_perm


from speedy.core.im.models import Chat
from speedy.match.likes.models import UserLike
from speedy.core.blocks.rules import is_blocked, is_self, has_blocked
from speedy.core.accounts.rules import has_access_perm


@predicate
def is_match_profile(user, other):
    if user.is_authenticated():
        match_profile = user.profile.matching_function(other_profile=other.profile) != 0
        has_message = Chat.on_site.filter((Q(ent1_id=user) & Q(ent1_id=other)) | (Q(ent1_id=other) & Q(ent2_id=user))).exists()
        has_likes = UserLike.objects.filter((Q(from_user=user) & Q(to_user=other)) | (Q(from_user=other) & Q(to_user=user)))
        return (user == other) or (match_profile or has_message or has_likes)
    return False


add_perm('accounts_match.view_profile', has_access_perm & ~is_blocked & ~has_blocked & is_match_profile)
add_perm('accounts_match.view_profile_info', has_access_perm & is_match_profile)
