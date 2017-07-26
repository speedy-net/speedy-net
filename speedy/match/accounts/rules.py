from django.db.models import Q

from rules import predicate, add_perm, remove_perm, always_allow

from .models import SiteProfile
from speedy.core.im.models import Chat
from speedy.match.likes.models import UserLike
from speedy.core.blocks.rules import there_is_block
from speedy.core.accounts.rules import has_access_perm


@predicate
def is_match_profile(user, other):
    if user.is_authenticated():
        match_profile = user.profile.get_matching_rank(other_profile=other.profile) > SiteProfile.RANK_0
        has_message = Chat.on_site.filter((Q(ent1_id=user) & Q(ent1_id=other)) | (Q(ent1_id=other) & Q(ent2_id=user))).exists()
        has_likes = UserLike.objects.filter((Q(from_user=user) & Q(to_user=other)) | (Q(from_user=other) & Q(to_user=user)))
        return (user == other) or (match_profile or has_message or has_likes)
    return False


remove_perm('accounts.view_profile')
add_perm('accounts.view_profile', has_access_perm & ~there_is_block & is_match_profile)
remove_perm('accounts.view_profile_header')
add_perm('accounts.view_profile_header', has_access_perm & is_match_profile)
remove_perm('accounts.view_profile_info')
add_perm('accounts.view_profile_info', has_access_perm & is_match_profile)
remove_perm('accounts.view_profile_age')
add_perm('accounts.view_profile_age', always_allow)
